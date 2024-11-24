gcloud compute routers nats update default-router   --router=default-nat   --region=asia-east1   --nat-external-ip-pool=external-ip-2   --nat-all-subnet-ip-ranges   --enable-endpoint-independent-mapping
gcloud compute addresses delete external-ip-1 --region=asia-east1
gcloud compute addresses create external-ip-1 --region=asia-east1
gcloud compute routers nats update default-router   --router=default-nat   --region=asia-east1   --nat-external-ip-pool=external-ip-1   --nat-all-subnet-ip-ranges   --enable-endpoint-independent-mapping
gcloud compute addresses delete external-ip-2 --region=asia-east1
gcloud compute addresses create external-ip-2 --region=asia-east1
