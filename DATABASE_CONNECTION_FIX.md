# Database Connection Troubleshooting Guide

## Issues Fixed ✅

### 1. **Password Mismatch** (CRITICAL)
- ❌ Was: `backend-deployment.yaml` had `Smartpay123`
- ❌ Was: `secret.yaml` had `Smartpay123#` (extra # character)
- ✅ Fixed: Both now use `Smartpay123` consistently

### 2. **Credentials Exposed** (SECURITY RISK)
- ❌ Was: Hardcoded credentials in deployment YAML
- ✅ Fixed: Now using Kubernetes secrets properly
- Updated: `backend-deployment.yaml` to reference `smartpay-secret`

### 3. **Network Connectivity** (ROOT CAUSE)
The timeout error `110` means your EKS pod cannot reach the RDS database.

## Steps to Resolve Network Issue

### Step 1: Check RDS Security Group (AWS Console)
1. Go to AWS Console → RDS → Databases → Find your RDS instance
2. Click on the instance → Security group rules
3. **MUST have an inbound rule**:
   - Type: MySQL/Aurora
   - Protocol: TCP
   - Port: 3306
   - Source: Your EKS Security Group ID

### Step 2: Find Your EKS Security Group
```bash
# Get the security group of your EKS nodes/pods
aws eks describe-cluster --name <your-cluster-name> --region ap-south-1 \
  --query 'cluster.resourcesVpcConfig.securityGroupIds' --output text
```

### Step 3: Add RDS Inbound Rule (if missing)
In AWS Console → RDS Security Group → Edit inbound rules:
- Click "Add rule"
- Type: MySQL/Aurora (3306)
- Source: Choose "Security Group" → Select EKS security group ID
- Save

**Alternative (AWS CLI)**:
```bash
aws ec2 authorize-security-group-ingress \
  --group-id <RDS-SECURITY-GROUP-ID> \
  --protocol tcp \
  --port 3306 \
  --source-group <EKS-SECURITY-GROUP-ID> \
  --region ap-south-1
```

### Step 4: Apply Updated Kubernetes Configs
```bash
# Delete and recreate the secret (to ensure it's updated)
kubectl delete secret smartpay-secret -n smartpay 2>/dev/null || true
kubectl apply -f k8s/secret.yaml

# Rollout the new deployment with corrected env vars
kubectl rollout restart deployment/backend -n smartpay

# Wait for pods to be ready
kubectl rollout status deployment/backend -n smartpay

# Watch logs for connection
kubectl logs -f deployment/backend -n smartpay
```

### Step 5: Verify Connection
```bash
# Test from inside the pod
kubectl run mysql-client --rm -it \
  --image=mysql:8.0 \
  --restart=Never \
  --namespace smartpay \
  -- mysql -h smartpay-mysql-rds.c3yc888c4lqk.ap-south-1.rds.amazonaws.com \
       -u admin \
       -p'Smartpay123'

# Should see: mysql> (not ERROR 2003)
```

## Quick Checklist

- [ ] Fixed password mismatch (Smartpay123 - no #)
- [ ] Updated backend-deployment.yaml to use secrets
- [ ] Verified RDS security group allows port 3306 from EKS
- [ ] Applied new configs: `kubectl apply -f k8s/secret.yaml && kubectl apply -f k8s/backend-deployment.yaml`
- [ ] Restarted pods: `kubectl rollout restart deployment/backend -n smartpay`
- [ ] Verified connection from test pod
- [ ] Sent money via frontend and checked database

## If Still Not Working

Check these in order:
```bash
# 1. Are the secrets properly loaded?
kubectl get secret smartpay-secret -n smartpay -o yaml

# 2. Do the pods have the right env vars?
kubectl exec -it deployment/backend -n smartpay -- env | grep MYSQL

# 3. Are pods actually running?
kubectl get pods -n smartpay

# 4. Check pod logs for connection errors
kubectl logs deployment/backend -n smartpay --tail=50

# 5. Is RDS publicly accessible? (if needed)
kubectl run mysql-test --rm -it --image=mysql:8.0 --restart=Never \
  -- mysql -h smartpay-mysql-rds.c3yc888c4lqk.ap-south-1.rds.amazonaws.com \
         -u admin -p'Smartpay123' -e "SELECT VERSION();"
```

## Expected Success
- ✅ Pod logs show: "✅ Connected to MySQL"
- ✅ Data inserted from frontend appears in database
- ✅ `/transactions` endpoint returns data
