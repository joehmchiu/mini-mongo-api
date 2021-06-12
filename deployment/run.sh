#!/bin/sh

# test 002
workdir=$1
LOG=$2
[ -z $LOG ] || rm -f $LOG

export PATH="$PATH:/usr/local/bin"

nn=0

function say {
  ((nn=$nn+1))
  echo "[$(date +'%F %T')] $nn. $1" >> $LOG
  sleep 1
}
say "restart minikube"
minikube stop && minikube delete && minikube start --vm=true --driver=hyperkit

say "repo: cd $workdir"
cd $workdir

say "evaluate and localize docker environment"
# eval $(minikube docker-env)
eval $(minikube -p minikube docker-env)
say "build docker image"
docker build . -t mongo-api

say "deploy docker image to kubernetes cluster"
kubectl create -f mini-mongo-deployment.yml
say "scale the replica sets"
kubectl scale deploy mongo-api --replicas 3
for i in {1..5}; do kubectl get deploy,po; sleep 3; done

say "expose the deployment service"
kubectl expose deploy mongo-api --type="LoadBalancer" --target-port=8600 --load-balancer-ip='192.168.64.16'

URL=$(minikube service --url mongo-api)
say "dump $URL to /tmp/url"
echo $URL > /tmp/url
say "dump $URL/api/v1/users/ to /tmp/api"
echo "$URL/api/v1/users/" > /tmp/api

PO=$(kubectl get pods | tail -n1 | awk '{print $1}')
say "forwarding POD: $PO port from 8600 to 9090"
/usr/bin/nohup kubectl port-forward $PO 9090:8600 &

say "DONE"
