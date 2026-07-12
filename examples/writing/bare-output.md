Subject: Service Disruption Post-Incident Notification

Dear Valued Customer,

We are writing to inform you that on the afternoon of the 11th, our
platform experienced a service degradation event affecting the checkout
subsystem. The root cause was identified as an expired TLS certificate in
our payment gateway's edge termination layer, which caused SSL handshake
failures for a subset of transactions. Our engineering team was paged
immediately and rotated the certificate, restoring full service. We have
implemented additional certificate-expiry monitoring and alerting to
prevent recurrence, and we are conducting a full post-mortem review of our
PKI lifecycle management processes.

We sincerely apologize for any inconvenience this may have caused and
thank you for your continued trust in our platform. Should you have any
questions, please do not hesitate to reach out to our support organization
through the usual channels.

Sincerely,
The Team
