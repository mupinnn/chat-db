import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { LoaderIcon } from "lucide-react";
import { marked } from "marked";
import { Button } from "./ui/button";
import { toast } from "sonner";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "./ui/sheet";
import {
  InputGroup,
  InputGroupTextarea,
  InputGroupButton,
  InputGroupAddon,
} from "./ui/input-group";

type ChatPayload = {
  q: string;
};

type ChatResponse = {
  message: string;
  data: string;
};

export function ChatSheet({ trigger }: { trigger: React.ReactNode }) {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<Array<{ q: string; a: string }>>([]);

  const chatMutation = useMutation<ChatResponse, Error, ChatPayload>({
    async mutationFn(chat) {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/ask`, {
        method: "POST",
        body: JSON.stringify(chat),
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (!response.ok) throw new Error("Something went wrong");
      return response.json();
    },
  });

  function sendQuestion() {
    chatMutation.mutate(
      { q: question },
      {
        onSuccess(data) {
          setQuestion("");
          setHistory((prev) => {
            return [...prev, { q: question, a: data.data }];
          });
        },
        onError(error) {
          toast.error(error.message);
        },
      },
    );
  }

  return (
    <Sheet>
      <SheetTrigger asChild>{trigger}</SheetTrigger>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Ask - Coffee Sales</SheetTitle>
          <SheetDescription>
            You can ask anything regarding the coffee sales data from the table
            and expect to return a human-friendly response.
          </SheetDescription>
        </SheetHeader>

        <div className="grid flex-1 auto-rows-min gap-6 px-4 overflow-auto">
          {history.map((h, i) => (
            <div key={i} className="flex flex-col gap-2">
              <div className="rounded p-2 self-end bg-primary text-primary-foreground w-fit">
                {h.q}
              </div>
              <div
                className="rounded p-2 self-start bg-muted w-fit"
                dangerouslySetInnerHTML={{
                  __html: marked.parse(h.a),
                }}
              />
            </div>
          ))}
        </div>

        <SheetFooter>
          <InputGroup>
            <InputGroupTextarea
              placeholder="Ask, Search or Chat..."
              value={question}
              readOnly={chatMutation.isPending}
              onChange={(e) => setQuestion(e.target.value)}
            />
            <InputGroupAddon align="block-end" className="justify-end">
              {chatMutation.isPending && (
                <LoaderIcon className="animate-spin" />
              )}
              <InputGroupButton
                variant="default"
                size="sm"
                disabled={chatMutation.isPending}
                onClick={sendQuestion}
              >
                Ask
              </InputGroupButton>
            </InputGroupAddon>
          </InputGroup>
          <SheetClose asChild>
            <Button variant="outline">Close</Button>
          </SheetClose>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}
