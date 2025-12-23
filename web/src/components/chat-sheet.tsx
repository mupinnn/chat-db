import { Button } from "./ui/button";
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

export function ChatSheet({ trigger }: { trigger: React.ReactNode }) {
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

        <div className="grid flex-1 auto-rows-min gap-6 px-4"></div>

        <SheetFooter>
          <InputGroup>
            <InputGroupTextarea placeholder="Ask, Search or Chat..." />
            <InputGroupAddon align="block-end">
              <InputGroupButton variant="default" size="sm" className="ml-auto">
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
