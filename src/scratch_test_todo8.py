import asyncio
import time
from assignment.pipeline import is_egress_allowed
from assignment.rate_limiter import RateLimitPlugin
from assignment.monitoring import MonitoringAlert
from assignment.audit_log import AuditLogPlugin

class DummyContext:
    user_id = "test_user_1"

async def main():
    print("=== Testing Egress ===")
    print("Valid URL & payload:", is_egress_allowed("https://api.vinbank.vn/transfer", "amount=100"))
    print("Invalid URL:", is_egress_allowed("https://hacker.com/dump", "amount=100"))
    print("PII in payload (phone):", is_egress_allowed("https://api.vinbank.vn/logs", "phone is 0901234567"))
    print("PII in payload (API key):", is_egress_allowed("https://api.vinbank.vn/logs", "sk-secret-key-123"))

    print("\n=== Testing Rate Limiter (max 2 per sec) ===")
    rl = RateLimitPlugin(max_requests=2, window_seconds=1)
    ctx = DummyContext()
    for i in range(3):
        res = await rl.on_user_message_callback(invocation_context=ctx, user_message="hello")
        if res is None:
            print(f"Req {i+1}: Allowed")
        else:
            print(f"Req {i+1}: BLOCKED - {res.parts[0].text}")

    print("\n=== Testing Audit Log ===")
    audit = AuditLogPlugin()
    audit.record_input(user_id="u1", text="Hello", request_id="req1")
    audit.record_output(user_id="u1", text="Hi", request_id="req1", blocked=False)
    audit.export_json("outputs/test_audit.json")
    print(f"Audit log saved {len(audit.logs)} events.")

    print("\n=== Testing Monitoring ===")
    mon = MonitoringAlert(block_rate_threshold=0.5, rate_limit_hit_threshold=5, judge_fail_rate_threshold=0.3)
    mon.total_requests = 10
    mon.blocked_requests = 6
    mon.rate_limit_hits = 6
    mon.judge_checks = 10
    mon.judge_fails = 4
    alerts = mon.check_metrics()
    print("Generated Alerts:")
    for a in alerts:
        print(f" - {a.message} ({a.metric}: {a.value})")

if __name__ == "__main__":
    asyncio.run(main())
