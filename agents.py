from config import settings


class WealthAdvisorAgents:
    def __init__(self, client=None):
        self.client = client

    def get_fiduciary_profiler_agent(self):
        if self.client is None:
            return None
        return self.client.create_agent(
            name="Fiduciary Profiler Agent",
            system_prompt=(
                "You are a wealth management fiduciary. Analyze an IPS and portfolio "
                "for a suitability briefing. Never calculate trades or override policy constraints."
            ),
        )

    def generate_advisor_brief(self, agent_id: str, client_id: str, orders_summary: str) -> str:
        if self.client is None:
            return f"Review required for client {client_id}: {orders_summary}"
        response = self.client.run_agent(agent_id=agent_id, message=f"Client {client_id}; orders: {orders_summary}")
        return response.get("content", "Briefing generation completed.")
