static type: string = "AccessDenied";
static type: string = "AccountNotLinked";
[auth][debug]: adapter_getUserByEmail
{ "args": [undefined] }
static type: string = "AdapterError";
optional cause: Record<string, unknown> & {
  err: Error;
};
optional err: Error;
type: ErrorType;
[auth][details]: { "provider": "github" }
static type: string = "CallbackRouteError";
code: string = "credentials";
static type: string = "CredentialsSignin";
static type: string = "DuplicateConditionalUI";
static type: string = "EmailSignInError";
static type: string = "ErrorPageLoop";
static type: string = "EventError";
static type: string = "ExperimentalFeatureNotEnabled";
static type: string = "InvalidCallbackUrl";
static type: string = "InvalidCheck";
static type: string = "InvalidEndpoints";
static type: string = "JWTSessionError";
static type: string = "MissingAdapter";
static type: string = "MissingAdapterMethods";
static type: string = "MissingCSRF";
static type: string = "MissingSecret";
static type: string = "OAuthAccountNotLinked";
static type: string = "OAuthProfileParseError";
[auth][details]: { "provider": "github" }
static type: string = "OAuthSignInError";
static type: string = "SessionTokenError";
static type: string = "SignOutError";
static type: string = "UnknownAction";
static type: string = "UnsupportedStrategy";
static type: string = "UntrustedHost";
static type: string = "Verification";
static type: string = "WebAuthnVerificationError";
