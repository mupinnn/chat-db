import { type ColumnDef } from "@tanstack/react-table";
import { MessageCircleIcon } from "lucide-react";
import { DataTable } from "./components/data-table";
import { Button } from "./components/ui/button";
import { ChatSheet } from "./components/chat-sheet";

type CoffeeSales = {
  date: string;
  datetime: string;
  cash_type: "card" | "cash";
  card: string;
  money: number;
  coffee_name: string;
};

const coffeSales: CoffeeSales[] = [
  {
    date: "2024-03-01",
    datetime: "2024-03-01 10:15:50.520",
    cash_type: "card",
    card: "ANON-0000-0000-0001",
    money: 38.7,
    coffee_name: "Latte",
  },
];

const columns: ColumnDef<CoffeeSales>[] = [
  {
    accessorKey: "datetime",
    header: "Date",
  },
  {
    accessorKey: "cash_type",
    header: "Payment Type",
  },
  {
    accessorKey: "money",
    header: "Price",
  },
  {
    accessorKey: "coffee_name",
    header: "Coffee Name",
  },
];

export function App() {
  return (
    <div className="3xl:max-w-screen-2xl mx-auto max-w-[1400px] p-4 lg:p-8 flex flex-1 scroll-mt-20 flex-col gap-4">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight">
          Coffee Sales Datasets
        </h1>
        <p className="text-muted-foreground">
          Datasets of coffee sales in a vending machine from{" "}
          <a
            href="https://www.kaggle.com/datasets/ihelon/coffee-sales"
            target="_blank"
            rel="noopener noreferrer"
            className="underline"
          >
            @ihelon/coffee-sales
          </a>
        </p>
      </div>

      <div className="flex items-center justify-end gap-4">
        <ChatSheet
          trigger={
            <Button>
              <MessageCircleIcon />
              Ask this table
            </Button>
          }
        />
      </div>

      <DataTable columns={columns} data={coffeSales} />
    </div>
  );
}
