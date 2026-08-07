// ... earlier code omitted for brevity ...
    console.error(
      `Unhandled error in chat API:${siteUrl}/api/chat`,
      error,
      {
        vercelId,
      }
    );
    return new ChatSDKError("offline:chat").toResponse();
// ...