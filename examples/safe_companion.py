"""Run with: python examples/safe_companion.py (after installing the package).

A synthetic demo only. A real UI obtains selected IDs from the human, never
from an autonomous model. No existing application data is opened here.
"""
from tempfile import TemporaryDirectory
from mistik_memory import Companion, LongTermMemory


def main():
    with TemporaryDirectory() as directory:
        memory = LongTermMemory(f'{directory}/memory.json')
        companion = Companion(memory)
        assert companion.confirm('The user lives in Berlin.')['ok']
        assert companion.confirm('The user lives in Paris.')['ok']
        print(memory.answer('Where does the user live?')['answer'])
        proposal = companion.propose_correction("That's wrong, Paris")
        print('Proposal only:', proposal['matched'])
        # Simulates a user's selection in this synthetic demonstration:
        selected = [h['fact_id'] for h in proposal['matched']]
        result = companion.apply_correction(proposal['proposal_id'], fact_ids=selected)
        assert result['ok']
        assert memory.fact_texts() == []
        assert memory.add_inferred_fact('The user lives in Paris.')['status'] == 'rejected'
        print('Selected fact forgotten; re-inference blocked; old city not revived.')


if __name__ == '__main__':
    main()
