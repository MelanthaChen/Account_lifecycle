import { Dialog } from "./ui/dialog";
import { AccountForm } from "./AccountForm";
import type { Account, AccountInput } from "../types/account";

interface AccountDialogProps {
  account?: Account | null;
  isPending?: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (input: AccountInput) => void;
  open: boolean;
}

export function AccountDialog({
  account,
  isPending,
  onOpenChange,
  onSubmit,
  open
}: AccountDialogProps) {
  const isEditing = Boolean(account);

  return (
    <Dialog
      open={open}
      onOpenChange={onOpenChange}
      title={isEditing ? "Edit account" : "Add account"}
      description="Manage the account record used by the intelligence workspace."
    >
      <AccountForm account={account} isPending={isPending} onSubmit={onSubmit} />
    </Dialog>
  );
}
