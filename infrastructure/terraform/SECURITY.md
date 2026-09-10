# Terraform Security Decisions

The AWS Terraform configuration is scanned with Trivy for HIGH and CRITICAL
misconfigurations.

## Accepted static-analysis exceptions

### AVD-AWS-0053 — public Application Load Balancer

The Application Load Balancer is intentionally internet-facing because it is
the HTTPS origin for CloudFront.

Compensating controls:

- ALB ingress is restricted to the AWS-managed CloudFront origin-facing prefix list.
- Only TCP/443 is accepted.
- The ALB listener uses HTTPS with an ACM certificate.
- CloudFront redirects viewer traffic to HTTPS.
- Backend ECS tasks accept port 8000 only from the ALB security group.

### AVD-AWS-0104 — ECS outbound HTTPS

Application tasks require outbound HTTPS for approved third-party APIs and AWS
public service endpoints.

Compensating controls:

- Internet egress is TCP/443 only.
- PostgreSQL egress is separately restricted to the RDS security group.
- Redis egress is separately restricted to the Redis security group.
- DNS traffic is separately restricted to the VPC CIDR.
- No unrestricted all-protocol internet egress rule is present.

These exceptions are scoped to the individual Terraform resources with Trivy
inline-ignore annotations. New HIGH or CRITICAL findings remain blocking.
