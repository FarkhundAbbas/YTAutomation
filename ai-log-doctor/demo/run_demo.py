#!/usr/bin/env python
"""Demo script to ingest sample logs and demonstrate self-healing."""
import sys
import os
import requests
import time

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
DETECTOR_BASE = os.getenv("DETECTOR_BASE", "http://localhost:8002")


def login():
    """Login and get token."""
    print("🔐 Logging in...")
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful!")
        return token
    else:
        print("❌ Login failed!")
        sys.exit(1)


def ingest_logs(log_file, token):
    """Ingest logs from file."""
    print(f"\n📥 Ingesting logs from {log_file}...")
    
    if not os.path.exists(log_file):
        print(f"❌ File not found: {log_file}")
        return None
    
    with open(log_file, 'r') as f:
        logs = [line.strip() for line in f if line.strip()]
    
    print(f"   Found {len(logs)} logs")
    
    # Send to detector
    response = requests.post(
        f"{DETECTOR_BASE}/detect-errors",
        json={"logs": logs, "platform": "generic"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        error_groups = response.json()
        print(f"✅ Created {len(error_groups)} error groups")
        return error_groups
    else:
        print(f"❌ Failed to ingest logs: {response.text}")
        return None


def generate_fix(error_group_id, token):
    """Generate fix for error group."""
    print(f"\n🤖 Generating AI fix for error group #{error_group_id}...")
    
    response = requests.post(
        f"{API_BASE}/proposals/create",
        params={"error_group_id": error_group_id, "platform": "generic"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        proposal = response.json()
        proposal_id = proposal["proposal_id"]
        print(f"✅ Proposal created! ID: {proposal_id}")
        print(f"\n   Generated {len(proposal['candidates'])} pattern candidates:")
        
        for i, candidate in enumerate(proposal['candidates']):
            print(f"\n   Candidate {i + 1}:")
            print(f"   Pattern: {candidate['pattern'][:80]}...")
            print(f"   Type: {candidate['pattern_type']}")
            print(f"   Confidence: {candidate['confidence']:.2f}")
        
        return proposal_id
    else:
        print(f"❌ Failed to generate fix: {response.text}")
        return None


def approve_proposal(proposal_id, pattern_index, token):
    """Approve a proposal."""
    print(f"\n✅ Approving proposal #{proposal_id}, pattern {pattern_index}...")
    
    response = requests.post(
        f"{API_BASE}/proposals/{proposal_id}/approve",
        json={"pattern_index": pattern_index, "user": "admin"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        print("✅ Proposal approved!")
        return True
    else:
        print(f"❌ Failed to approve: {response.text}")
        return False


def apply_fix(proposal_id, token):
    """Apply the fix."""
    print(f"\n🚀 Applying fix for proposal #{proposal_id}...")
    
    response = requests.post(
        f"{API_BASE}/apply/{proposal_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Fix applied! Rule ID: {result['rule_id']}")
        return result['rule_id']
    else:
        print(f"❌ Failed to apply fix: {response.text}")
        return None


def get_stats(token):
    """Get dashboard stats."""
    print("\n📊 Dashboard Statistics:")
    
    response = requests.get(
        f"{API_BASE}/stats/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        stats = response.json()
        print(f"   Error Groups: {stats['total_error_groups']}")
        print(f"   Pending Proposals: {stats['pending_proposals']}")
        print(f"   Applied Fixes: {stats['applied_fixes']}")
        print(f"   Active Rules: {stats['active_rules']}")
    else:
        print(f"❌ Failed to get stats: {response.text}")


def main():
    """Main demo workflow."""
    print("=" * 70)
    print(" AI LOG DOCTOR - DEMO ")
    print("=" * 70)
    
    # Login
    token = login()
    
    # Ingest logs
    log_file = sys.argv[1] if len(sys.argv) > 1 else "samples/sample_logs.txt"
    error_groups = ingest_logs(log_file, token)
    
    if not error_groups:
        print("\n❌ No error groups created. Exiting.")
        return
    
    # Generate fix for first error group
    first_group = error_groups[0]
    proposal_id = generate_fix(first_group["error_group_id"], token)
    
    if not proposal_id:
        print("\n❌ Failed to generate proposal. Exiting.")
        return
    
    # Approve first pattern
    if approve_proposal(proposal_id, 0, token):
        # Apply the fix
        rule_id = apply_fix(proposal_id, token)
        
        if rule_id:
            print("\n🎉 Self-healing workflow complete!")
    
    # Show final stats
    get_stats(token)
    
    print("\n" + "=" * 70)
    print("✅ Demo completed successfully!")
    print("   Visit http://localhost:3000 to see the dashboard")
    print("=" * 70)


if __name__ == "__main__":
    main()
