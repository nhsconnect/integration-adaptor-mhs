# Target group for the application load balancer for MHS outbound
# The MHS outbound ECS service registers it's tasks here.
resource "aws_lb_target_group" "fake_spine_alb_target_group" {
  port = 80
  protocol = "HTTP"
  target_type = "ip"
  vpc_id = data.terraform_remote_state.mhs.vpc_id

  health_check {
    path = "/healthcheck"
    matcher = "200"
  }

  tags = {
    Name = "${var.environment_id}-fake-spine-alb-target-group"
    EnvironmentId = var.environment_id
  }
}