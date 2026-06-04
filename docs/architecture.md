# ParkSmart Architecture Diagram

```text
                        +----------------------+
                        |      GitHub Repo     |
                        +----------------------+
                                   |
                                   | Push Code
                                   v
                        +----------------------+
                        |   GitHub Actions     |
                        |  (OIDC Authentication)|
                        +----------------------+
                                   |
                                   v
                        +----------------------+
                        |  Artifact Registry   |
                        +----------------------+
                                   |
                                   v
                        +----------------------+
                        |      Cloud Run       |
                        |     Flask App        |
                        +----------------------+
                              |          |
                              |          |
                              v          v
                    +---------------+  +----------------+
                    |  Cloud SQL    |  | Secret Manager |
                    | PostgreSQL DB |  | DB Passwords   |
                    +---------------+  +----------------+

             +------------------------------------+
             |          ParkSmart VPC             |
             |  Cloud Run + Cloud SQL Network     |
             +------------------------------------+

                        +----------------------+
                        |        Users         |
                        | Web Browser Access   |
                        +----------------------+
                                   |
                                   v
                        +----------------------+
                        |      Cloud Run       |
                        +----------------------+
```