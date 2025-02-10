# ssh -i "stock.pem" ec2-user@ec2-35-176-222-6.eu-west-2.compute.amazonaws.com
# ssh -o ControlMaster=no -i "stock.pem" ec2-user@ec2-35-176-222-6.eu-west-2.compute.amazonaws.com
ssh -o ControlMaster=no -o "SendEnv TERM" -i "../stock.pem" ec2-user@ec2-35-176-222-6.eu-west-2.compute.amazonaws.com
