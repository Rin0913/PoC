while :; do
    regions=("asia-east1" "asia-east2" "asia-south1")
    {
        for region in "${regions[@]}"; do
            echo $region
            gcloud compute addresses create external-ip-2 --region=$region
            gcloud compute routers nats update default-router   --router=default-nat   --region=$region   --nat-external-ip-pool=external-ip-2   --nat-all-subnet-ip-ranges   --enable-endpoint-independent-mapping
            gcloud compute addresses delete external-ip-1 --region=$region --quiet
            gcloud compute addresses create external-ip-1 --region=$region
            gcloud compute routers nats update default-router   --router=default-nat   --region=$region   --nat-external-ip-pool=external-ip-1   --nat-all-subnet-ip-ranges   --enable-endpoint-independent-mapping
            gcloud compute addresses delete external-ip-2 --region=$region --quiet
        done
    } &
    sleep 60
done
