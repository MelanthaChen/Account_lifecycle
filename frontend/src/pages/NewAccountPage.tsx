import { useNavigate } from "react-router-dom";

import { AccountForm } from "../components/AccountForm";
import { useCreateAccount } from "../hooks/useAccounts";

export function NewAccountPage() {
  const navigate = useNavigate();
  const createAccount = useCreateAccount();

  return (
    <div className="mx-auto max-w-3xl space-y-5">
      <div className="border-b border-border pb-5">
        <h1 className="text-2xl font-semibold">Add Reddit Account</h1>
        <p className="mt-1 text-sm text-muted-foreground">Create a managed account record.</p>
      </div>
      <div className="rounded-md border border-border bg-white p-5">
        <AccountForm
          isPending={createAccount.isPending}
          onSubmit={(input) =>
            createAccount.mutate(input, {
              onSuccess: (account) => navigate(`/accounts/${account.id}`)
            })
          }
        />
      </div>
    </div>
  );
}
