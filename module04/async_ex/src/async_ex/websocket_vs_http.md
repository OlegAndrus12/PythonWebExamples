| Feature           | HTTP                                                              | WebSocket                                                       |
| ----------------- | ----------------------------------------------------------------- | --------------------------------------------------------------- |
| **Communication** | Request → Response (client initiates)                             | Full-duplex (both sides can send at any time)                   |
| **Connection**    | Short-lived; closes after response                                | Long-lived; stays open                                          |
| **Use case**      | Web pages, APIs, form submission                                  | Chat, live feeds, notifications, real-time games                |
| **Overhead**      | Every request includes HTTP headers                               | Initial handshake uses HTTP headers; then minimal framing       |
| **Latency**       | Higher for frequent updates (each request creates new connection) | Low latency; messages sent instantly over persistent connection |
| **Server push**   | Not possible directly; need polling or SSE                        | Server can push data anytime                                    |
