import { useMutation } from "@tanstack/react-query";

import { createCommentRequest } from "../api/comment";

export function useCreateCommentRequest() {
  return useMutation({ mutationFn: createCommentRequest });
}
