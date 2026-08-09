QUESTIONS = {
    "aws-vpc": [
        {"question": "What is an AWS VPC, and what problem does it solve?",
         "rubric": ["logical network isolation", "IP address range", "subnets", "routing", "network security"]},
        {"question": "How do you determine whether an AWS subnet is public or private?",
         "rubric": ["route table", "internet gateway", "default route", "public IP distinction"]},
        {"question": "An EC2 instance is in a public subnet but you cannot SSH to it. Walk me through your investigation.",
         "rubric": ["public IP", "route table", "internet gateway", "security group", "NACL", "instance/sshd", "local firewall"]},
        {"question": "Why would an application use private subnets, and how can private instances reach the internet?",
         "rubric": ["reduced exposure", "NAT gateway", "public subnet for NAT", "route tables", "internet gateway"]},
        {"question": "A private EC2 instance cannot download package updates. Give me your top hypotheses and the evidence you would collect.",
         "rubric": ["NAT gateway", "private route table", "NAT public route", "internet gateway", "security group", "NACL", "DNS"]},
        {"question": "Explain the difference between a Security Group and a Network ACL.",
         "rubric": ["stateful", "stateless", "instance/ENI", "subnet", "inbound/outbound", "return traffic"]},
        {"question": "Users report intermittent 504 errors from an internet-facing ALB. How would you investigate?",
         "rubric": ["ALB metrics", "target health", "target response time", "security groups", "application logs", "network path"]},
        {"question": "A production deployment changed a route table and traffic stopped reaching the application. How would you prove the route is the root cause?",
         "rubric": ["route table association", "destination", "target", "longest prefix", "flow logs", "controlled test", "rollback"]},
    ]
}

def get_questions(topic: str):
    return QUESTIONS.get(topic.lower().replace(" ", "-"), QUESTIONS["aws-vpc"])
