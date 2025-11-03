## cluster setup
1. open AWS Cloud Shell

    export CLUSTER_NAME=nim-eks-workshop
    export CLUSTER_NODE_TYPE=g6e.xlarge
    export NODE_COUNT=1

2. eksctl create cluster --name=$CLUSTER_NAME --node-type=$CLUSTER_NODE_TYPE --nodes=$NODE_COUNT

3. kubectl get nodes -o wide


## storage
4.  eksctl utils associate-iam-oidc-provider --cluster $CLUSTER_NAME --approve
5.  eksctl create iamserviceaccount \
  --name ebs-csi-controller-sa \
  --namespace kube-system \
  --cluster $CLUSTER_NAME \
  --role-name AmazonEKS_EBS_CSI_DriverRole \
  --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
  --approve

6.  eksctl create addon \
  --name "aws-ebs-csi-driver" \
  --cluster $CLUSTER_NAME\
  --region=$AWS_DEFAULT_REGION\
  --service-account-role-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/AmazonEKS_EBS_CSI_DriverRole\
  --force

7. check the status until it becomes available:

eksctl get addon \
 --name "aws-ebs-csi-driver" \
 --region $AWS_DEFAULT_REGION \
 --cluster $CLUSTER_NAME

8. cat <<EOF >  storage.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
    name: ebs-sc
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer
EOF

9. kubectl create -f storage.yaml 

10. export NGC_CLI_API_KEY=<YOUR NVIDIA API KEY>

11. install helm

12. helm fetch https://helm.ngc.nvidia.com/nim/charts/nim-llm-1.7.0.tgz --username='$oauthtoken' --password=$NGC_CLI_API_KEY

12. kubectl create namespace nim

13. kubectl create secret docker-registry registry-secret --docker-server=nvcr.io --docker-username='$oauthtoken'     --docker-password=$NGC_CLI_API_KEY -n nim

14. kubectl create secret generic ngc-api --from-literal=NGC_API_KEY=$NGC_CLI_API_KEY -n nim

15.
cat <<EOF > nim_custom_value.yaml
image:
  repository: "nvcr.io/nim/nvidia/llama-3.1-nemotron-nano-8b-v1" # container location
  tag: latest # NIM version you want to deploy
model:
  ngcAPISecret: ngc-api  # name of a secret in the cluster that includes a key named NGC_CLI_API>
persistence:
  enabled: true
  storageClass: "ebs-sc"
  accessMode: ReadWriteOnce
  stsPersistentVolumeClaimRetentionPolicy:
      whenDeleted: Retain
      whenScaled: Retain
imagePullSecrets:
  - name: registry-secret # name of a secret used to pull nvcr.io images, see https://kubernetes.io/docs/tasks/    configure-pod-container/pull-image-private-registry/
EOF


cat <<EOF > nim_custom_tool_parser.yaml
image:
  repository: "nvcr.io/nim/nvidia/llama-3.1-nemotron-nano-8b-v1"
  tag: latest
model:
  modelName: "llama-3.1-nemotron-nano-8b-v1"
  ngcAPISecret: ngc-api  
env:
  - name: NIM_ENABLE_AUTO_TOOL_CHOICE
    value: "1"
  - name: NIM_TOOL_CALL_PARSER
    value: "llama_nemotron_json"
persistence:
  enabled: true
  storageClass: "ebs-sc"
  accessMode: ReadWriteOnce
  stsPersistentVolumeClaimRetentionPolicy:
      whenDeleted: Retain
      whenScaled: Retain
imagePullSecrets:
  - name: registry-secret
EOF


16. helm install my-nim nim-llm-1.7.0.tgz -f nim_custom_value.yaml --namespace nim

17. check deployment status: kubectl get pods -n nim -w

17. kubectl -n nim port-forward service/my-nim-nim-llm 8000:8000

18. send a request

curl -X 'POST' \
  'http://a11abe82bd8da4ae79f6100bd89fa0f8-483808785.us-east-1.elb.amazonaws.com:8000/v1/chat/completions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "messages": [
    {
      "content": "detailed thinking off",
      "role": "system"
    },
    {
      "content": "What should I do for a 4 day vacation in Greece?",
      "role": "user"
    }
  ],
  "model": "nvidia/llama-3.1-nemotron-nano-8b-v1",
  "max_tokens": 128,
  "top_p": 1,
  "n": 1,
  "stream": false,
  "stop": "\n",
  "frequency_penalty": 0.0
}'

## Public API

1. check your pod name:
kubectl get svc -n nim

which returns something like:
NAME                 TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
my-nim-nim-llm       ClusterIP   10.100.98.223   <none>        8000/TCP   8m52s
my-nim-nim-llm-sts   ClusterIP   None            <none>        8000/TCP   8m52s

2. kubectl get svc my-nim-nim-llm -n nim -o yaml | grep "app.kubernetes.io"

which returns:
    app.kubernetes.io/instance: my-nim
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/name: nim-llm
    app.kubernetes.io/version: 1.0.3
    app.kubernetes.io/instance: my-nim << this is it
    app.kubernetes.io/name: nim-llm << this is it

3. create a file:
cat <<EOF > nim_public.yaml
apiVersion: v1
kind: Service
metadata:
  name: nim-public
  namespace: nim
spec:
  selector:
    app.kubernetes.io/name: nim-llm          
    app.kubernetes.io/instance: my-nim       
  ports:
    - name: http
      port: 8000
      targetPort: 8000
      protocol: TCP
  type: LoadBalancer
EOF

4. kubectl apply -f nim_public.yaml

5. kubectl get svc -n nim
returns:

NAME                 TYPE           CLUSTER-IP      EXTERNAL-IP                                                               PORT(S)          AGE
my-nim-nim-llm       ClusterIP      10.100.98.223   <none>                                                                    8000/TCP         12m
my-nim-nim-llm-sts   ClusterIP      None            <none>                                                                    8000/TCP         12m
nim-public           LoadBalancer   10.100.61.38    a51ca87ba811c40f4a082fe2be9ddcb0-1052556339.us-east-1.elb.amazonaws.com   8000:30607/TCP   24s

your public IP address: a51ca87ba811c40f4a082fe2be9ddcb0-1052556339.us-east-1.elb.amazonaws.com


6. check what models are available:
curl http://a11abe82bd8da4ae79f6100bd89fa0f8-483808785.us-east-1.elb.amazonaws.com:8000/v1/models



returns:
{"object":"list","data":[{"id":"nvidia/llama-3.1-nemotron-nano-8b-v1","object":"model","created":1761920148,"owned_by":"system","root":"nvidia/llama-3.1-nemotron-nano-8b-v1","parent":null,"max_model_len":131072,"permission":[{"id":"modelperm-05e6a9f8ee4343479cfbce1d30ac40bd","object":"model_permission","created":1761920148,"allow_create_engine":false,"allow_sampling":true,"allow_logprobs":true,"allow_search_indices":false,"allow_view":true,"allow_fine_tuning":false,"organization":"*","group":null,"is_blocking":false}]}]}

7. test your model

curl http://a51ca87ba811c40f4a082fe2be9ddcb0-1052556339.us-east-1.elb.amazonaws.com:8000/v1/chat/completions \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "model": "nvidia/llama-3.1-nemotron-nano-8b-v1",
  "messages": [
    {"role": "user", "content": "Say hi from Vancouver!"}
  ]
}'


curl -X POST http://a11abe82bd8da4ae79f6100bd89fa0f8-483808785.us-east-1.elb.amazonaws.com:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nvidia/llama-3.1-nemotron-nano-8b-v1",
    "messages": [
      {"role":"system","content":"detailed thinking off"},
      {"role":"user","content":"Call the get_weather tool for Tokyo"}
    ],
    "tools": [
      {
        "type":"function",
        "function": {
          "name":"get_weather",
          "description":"Get weather for a city",
          "parameters":{
            "type":"object",
            "properties":{
              "city":{"type":"string"}
            },
            "required":["city"]
          }
        }
      }
    ],
    "tool_choice": "auto"
  }'

5. Test tool calling: 
curl -X POST http://a11abe82bd8da4ae79f6100bd89fa0f8-483808785.us-east-1.elb.amazonaws.com:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nvidia/llama-3.1-nemotron-nano-8b-v1",
    "messages": [
      {"role":"system","content":"detailed thinking off"},
      {"role": "user", "content": "add 2 and 5 using the tool"}
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "calculate_sum",
          "description": "add two numbers",
          "parameters": {
            "type": "object",
            "properties": {
              "a": {"type": "integer"},
              "b": {"type": "integer"}
            },
            "required": ["a","b"]
          }
        }
      }
    ],
    "tool_choice": "auto"
  }'