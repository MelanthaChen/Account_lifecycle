import { AccountForm } from "../AccountForm";
import { useUpdateAccount } from "../../hooks/useAccounts";
import { useToast } from "../../store/useToast";
import type { Account, AccountInput } from "../../types/account";

export function AccountSettingsPanel({ account }: { account: Account }) {
  const updateAccount = useUpdateAccount();
  const { notify } = useToast();

  function handleSubmit(input: AccountInput) {
    updateAccount.mutate(
      { accountId: account.id, input },
      {
        onSuccess: () => notify("Account settings saved.", "success"),
        onError: () => notify("Unable to save account settings.", "error")
      }
    );
  }

  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-base font-semibold">Account Settings</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Update account metadata, status, and browser launch preferences.
        </p>
      </div>
      <div className="rounded-md border border-border bg-white p-5">
        <AccountForm account={account} onSubmit={handleSubmit} isPending={updateAccount.isPending} />
      </div>
    </section>
  );
}
