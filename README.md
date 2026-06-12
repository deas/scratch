## Persönliches Random ScratchPad - im Rahmen des ADR ignorieren

- Nachfragen (insbesondere was unklar ist)
- Prozess illustrieren
- Kritiker! (Fallstricke)
- Trade-Offs (Speed/Stability/Complexity/Generalization)/Alternativen
- Sync-Waves?

- "Alignment"

GitOps Repo/Prozess war Teil meines "Struktur" Alignment Planes Repos/Branches/Folders. Nun ist das "Testing" geworden, und wir haben zwei große Team Abstimmungen -> Kognitive Load -> Unsicherheit? Fairness?

- Plan: Jeder challenged ADR (z.B. mit LLM), Eine gemeinsame Roast Session
- Rückzug aus common operators? Too many chefs?
- "Sichtbarkeit" Branches vs. Folders
- Solution slopped by spec
- Propagation prozess?
- Kein A/B -> Progressive Rollout in Prod
- Kein Hot Standby (z.B. Admin)
- helm dance demo?
- branch/folder mapping "dev": Uniform?
- Wo (insbesondere Pipelines) werden state repos/branches/tags referenziert?
- Sync waves: Explizite Deps + Ordering vs. Retry (-> Concurrency/Speed)
- Alternatives argocd conductor Modell
- ApplicationSet?
- Kompatibilität mit Propagation Tools wie kargo?
- Helm Aggregation "Workaround" (values Propagation from root)?
- Pilot Monitoring/Observability Central vs. full Common-Operators?
- Auditability?
- Constraint Classes: ArgoCD, Security/Governance, On-Prem Infra/Umsysteme, Team Strukturen
- Was genau wurde reviewed?
- Cluster Bootstrap/Teardown Code wo hin?
