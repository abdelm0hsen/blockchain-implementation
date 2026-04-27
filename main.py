import hashlib
import json
import time
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class Block:
    index: int
    timestamp: float
    transactions: List[dict]
    previous_hash: str
    nonce: int = 0
    hash: str = ""

    def calculate_hash(self) -> str:
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }
        encoded = json.dumps(block_data, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class Blockchain:
    def __init__(self, difficulty: int = 3):
        self.difficulty = difficulty
        self.chain: List[Block] = [self.create_genesis_block()]
        self.pending_transactions: List[dict] = []

    def create_genesis_block(self) -> Block:
        genesis = Block(
            index=0,
            timestamp=time.time(),
            transactions=[{"from": "network", "to": "genesis", "amount": 0}],
            previous_hash="0",
        )
        genesis.hash = genesis.calculate_hash()
        return genesis

    def add_transaction(self, sender: str, receiver: str, amount: float) -> None:
        self.pending_transactions.append({"from": sender, "to": receiver, "amount": amount})

    def mine_pending_transactions(self, miner_address: str) -> Block:
        if not self.pending_transactions:
            raise ValueError("No transactions to mine")

        self.pending_transactions.append({"from": "network", "to": miner_address, "amount": 1.0})

        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=self.pending_transactions.copy(),
            previous_hash=self.chain[-1].hash,
        )

        target_prefix = "0" * self.difficulty
        while True:
            new_hash = new_block.calculate_hash()
            if new_hash.startswith(target_prefix):
                new_block.hash = new_hash
                break
            new_block.nonce += 1

        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True


def print_chain(chain: List[Block]) -> None:
    for block in chain:
        print(f"\nBlock #{block.index}")
        print(f"Timestamp: {block.timestamp}")
        print(f"Transactions: {block.transactions}")
        print(f"Previous Hash: {block.previous_hash}")
        print(f"Nonce: {block.nonce}")
        print(f"Hash: {block.hash}")


def main() -> None:
    blockchain = Blockchain(difficulty=3)

    while True:
        print("\nBlockchain Menu")
        print("1. Add transaction")
        print("2. Mine block")
        print("3. Show chain")
        print("4. Validate chain")
        print("5. Exit")
        choice = input("Select option: ").strip()

        if choice == "1":
            sender = input("Sender: ").strip()
            receiver = input("Receiver: ").strip()
            amount = float(input("Amount: ").strip())
            blockchain.add_transaction(sender, receiver, amount)
            print("[+] Transaction added.")
        elif choice == "2":
            miner = input("Miner address: ").strip() or "miner-1"
            try:
                block = blockchain.mine_pending_transactions(miner)
                print(f"[+] Block #{block.index} mined with hash {block.hash}")
            except ValueError as error:
                print(f"[!] {error}")
        elif choice == "3":
            print_chain(blockchain.chain)
        elif choice == "4":
            print("[+] Chain valid." if blockchain.is_chain_valid() else "[!] Chain invalid.")
        elif choice == "5":
            break
        else:
            print("[!] Invalid option.")


if __name__ == "__main__":
    main()
