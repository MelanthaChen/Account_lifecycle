import { useMutation } from "@tanstack/react-query";

import { createUpvoteRequest } from "../api/upvote";

export function useCreateUpvoteRequest() {
  return useMutation({ mutationFn: createUpvoteRequest });
}
