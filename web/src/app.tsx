import { useState } from "react";
import { type ColumnDef, functionalUpdate } from "@tanstack/react-table";
import { useQuery } from "@tanstack/react-query";
import { MessageCircleIcon, CircleQuestionMarkIcon } from "lucide-react";
import { DataTable } from "./components/data-table";
import { Button } from "./components/ui/button";
import { ChatSheet } from "./components/chat-sheet";
import {
  TooltipContent,
  TooltipTrigger,
  Tooltip,
} from "./components/ui/tooltip";

type CoffeeSales = {
  date: string;
  datetime: string;
  cash_type: "card" | "cash";
  card: string;
  money: number;
  coffee_name: string;
};

const columns: ColumnDef<CoffeeSales>[] = [
  {
    accessorKey: "datetime",
    header: "Date",
    cell: (props) =>
      new Intl.DateTimeFormat("en", {
        dateStyle: "long",
        timeStyle: "medium",
      }).format(new Date(props.row.original.datetime)),
  },
  {
    accessorKey: "cash_type",
    header: "Payment Type",
  },
  {
    accessorKey: "money",
    header: () => (
      <span className="flex items-center gap-2">
        Price
        <Tooltip>
          <TooltipTrigger>
            <CircleQuestionMarkIcon className="size-4" />
          </TooltipTrigger>
          <TooltipContent>
            The price is on Ukrainian hryvnia (UAH)
          </TooltipContent>
        </Tooltip>
      </span>
    ),
    cell: (props) =>
      new Intl.NumberFormat("uk", {
        style: "currency",
        currency: "UAH",
      }).format(props.row.original.money),
  },
  {
    accessorKey: "coffee_name",
    header: "Coffee Name",
  },
];

export function App() {
  const [pagination, setPagination] = useState({
    offset: 0,
    pageIndex: 0,
    pageSize: 25,
  });

  const { data } = useQuery({
    queryKey: ["sales", pagination],
    async queryFn() {
      const { offset } = pagination;
      const res = await fetch(
        `${import.meta.env.VITE_API_URL}/sales?offset=${offset}`,
      );
      return (await res.json()) as Promise<{
        data: CoffeeSales[];
        count: number;
        limit: number;
        offset: number;
      }>;
    },
  });

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
              Ask for "Most purchased coffe?"
            </Button>
          }
        />
      </div>

      <DataTable
        columns={columns}
        data={data?.data || []}
        pagination={{
          pageSize: pagination.pageSize,
          pageIndex: pagination.pageIndex,
        }}
        paginationOptions={{
          onPaginationChange: (updater) => {
            const newValue = functionalUpdate(updater, pagination);
            const offset = newValue.pageIndex * newValue.pageSize;
            const count = data?.count || 0;

            setPagination({
              ...newValue,
              offset: offset > count ? count - newValue.pageSize : offset,
            });
          },
          rowCount: data?.count,
        }}
      />
    </div>
  );
}
