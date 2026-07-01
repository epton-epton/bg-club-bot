export function ErrorState({ message }: { message: string }) {
  return <p className="state-message state-message--error">{message}</p>;
}
