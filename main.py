import json
from abc import ABC, abstractmethod

# 数据存储抽象层（依赖反转：业务逻辑依赖抽象，而非具体文本文件）
class DataStorage(ABC):
    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def save_data(self, data):
        pass

# 文本文件存储实现（具体实现类）
class TextFileStorage(DataStorage):
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_data(self, data):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

# 业务逻辑层（依赖抽象存储，与具体存储方式解耦）
class AirlineTicketSystem:
    def __init__(self, storage: DataStorage):
        self.storage = storage
        self.tickets = self.storage.load_data()

    # 创建机票
    def create_ticket(self, ticket_id, flight_num, origin, destination, date, price, seats_left):
        ticket = {
            "ticket_id": ticket_id,
            "flight_num": flight_num,
            "origin": origin,
            "destination": destination,
            "date": date,
            "price": float(price),
            "seats_left": int(seats_left)
        }
        self.tickets.append(ticket)
        self.storage.save_data(self.tickets)
        return "Ticket created successfully"

    # 查询机票（按出发地+目的地）
    def search_tickets(self, origin, destination):
        results = [t for t in self.tickets if t["origin"].lower() == origin.lower() and t["destination"].lower() == destination.lower()]
        return results if results else "No tickets found for this route"

    # 预订机票（减少剩余座位）
    def book_ticket(self, ticket_id):
        for ticket in self.tickets:
            if ticket["ticket_id"] == ticket_id:
                if ticket["seats_left"] > 0:
                    ticket["seats_left"] -= 1
                    self.storage.save_data(self.tickets)
                    return f"Ticket {ticket_id} booked successfully. Remaining seats: {ticket['seats_left']}"
                else:
                    return "No seats left for this ticket"
        return "Ticket not found"

# CLI交互层
def cli_interface():
    # 初始化文本文件存储（数据文件：tickets.json）
    storage = TextFileStorage("tickets.json")
    system = AirlineTicketSystem(storage)

    print("=== Airline Ticket Sales Information System ===")
    while True:
        print("\n1. Create Ticket\n2. Search Tickets\n3. Book Ticket\n4. Exit")
        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            ticket_id = input("Enter ticket ID: ")
            flight_num = input("Enter flight number: ")
            origin = input("Enter origin city: ")
            destination = input("Enter destination city: ")
            date = input("Enter flight date (YYYY-MM-DD): ")
            price = input("Enter ticket price: ")
            seats_left = input("Enter number of seats: ")
            print(system.create_ticket(ticket_id, flight_num, origin, destination, date, price, seats_left))

        elif choice == "2":
            origin = input("Enter origin city: ")
            destination = input("Enter destination city: ")
            results = system.search_tickets(origin, destination)
            if isinstance(results, list):
                for t in results:
                    print(f"\nID: {t['ticket_id']} | Flight: {t['flight_num']} | Date: {t['date']} | Price: {t['price']} | Seats Left: {t['seats_left']}")
            else:
                print(results)

        elif choice == "3":
            ticket_id = input("Enter ticket ID to book: ")
            print(system.book_ticket(ticket_id))

        elif choice == "4":
            print("Exiting system...")
            break

        else:
            print("Invalid choice. Please try again.")

# 单元测试（验证业务逻辑正确性）
import unittest

class TestAirlineTicketSystem(unittest.TestCase):
    def setUp(self):
        # 使用临时文本文件进行测试
        self.test_storage = TextFileStorage("test_tickets.json")
        self.system = AirlineTicketSystem(self.test_storage)

    def tearDown(self):
        import os
        if os.path.exists("test_tickets.json"):
            os.remove("test_tickets.json")

    def test_create_and_search_ticket(self):
        self.system.create_ticket("T001", "CA123", "Beijing", "Shanghai", "2024-12-01", 800, 10)
        results = self.system.search_tickets("Beijing", "Shanghai")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["flight_num"], "CA123")

    def test_book_ticket(self):
        self.system.create_ticket("T002", "MU456", "Guangzhou", "Shenzhen", "2024-12-02", 300, 5)
        book_result = self.system.book_ticket("T002")
        self.assertIn("booked successfully", book_result)
        self.assertEqual(self.system.tickets[0]["seats_left"], 4)

if __name__ == "__main__":
    # 运行CLI或单元测试（通过命令行参数控制）
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        unittest.main()
    else:
        cli_interface()