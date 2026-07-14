APPROACH: Cache per-entity fragments with version-keyed invalidation instead of whole responses to prevent stale data in dependent services like checkout.

AVOID: Caching whole responses in Redis; cache invalidation bugs produced stale order totals in checkout and the approach was abandoned.