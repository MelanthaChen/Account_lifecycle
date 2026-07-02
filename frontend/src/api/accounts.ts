import { api } from "./client";
import type { Account, AccountInput } from "../types/account";

export async function listAccounts() {
  const response = await api.get<Account[]>("/accounts");
  return response.data;
}

export async function createAccount(input: AccountInput) {
  const response = await api.post<Account>("/accounts", input);
  return response.data;
}

export async function updateAccount(accountId: string, input: Partial<AccountInput>) {
  const response = await api.patch<Account>(`/accounts/${accountId}`, input);
  return response.data;
}

export async function deleteAccount(accountId: string) {
  await api.delete(`/accounts/${accountId}`);
}
