# Monitoring Helm Deployments

Wir betrachten hier nur Observability/Monitoring.

- Was war das Ziel des Helm Epics? Meine Erwartung war Helm-Native first, möglichst Cloud Agnostic und möglichst Vendor Blueprints (Helm Charts) as is nutzen -> Maintainance
- Jinja2 Manifest "Retrofit" war erwartet/gewünscht? imho irreführend für Helm-Natives die Historie nicht kennen (Onboarding)
- Nun: Zwischen zwei Welten?

## Betrachtung ArgoCD App und Helm Releases in sources

- Helm charts nutzen values-sample.yaml Muster für mehrere Namespaces (kein `Release.Namespace`)
- Vorgabe Übergabe `clusterName` durch helm sources macht direkte Nutzung von Upstream charts schwieriger (FQNs / Adapter Code / Chart Author muss dafür `tpl` Unterstützung vorgesehen haben) -> Eher Forking?
- kustomized-helm würde Forks mindestens in Teilen ersetzen, vielleicht komplett Upstream sinnvoll möglich machen.
- Subcharts: Nutzung exploded + packaged (Chart.yml) schwierig implementierbar, "Lösung" Vendoring unerwünscht
- Chart Releases in ArgoCD sources haben intransparente Abhängigkeiten? (`prometheus` chart erzeugt z.B. Namespace für alle die nutzen)
- `--CreateNamespace: false`, `destination.namespace: ... (Release.Namespace)`: Irreführend für Helm-Natives, wenn "intransparent" `namespace: {...}` genutzt wird?
- Mandatory Namespace template mit privileged Annotation "unkonventionell" (-> `CreateNamespace: false`)
- ArgoCD Annotations (sync wave) in helm?
- "Single" Use Case Values in Charts? (aktuell fast nur noch On-Prem?)

## Diverses

- AD Hacks in dex chart, weil Einträge erst nach Datenbank Erstellung gemacht werden
- Irreführende, Nicht aussagekräftige Mails von Konvoi (OPS4PCBW-1434), keine Aussagekraft - muss in Nexus geprüft werden (OCI hat das Problem nicht)
- Chart Umzug: Keine Chart Pipeline auf On-Prem gitlab (Existiert auf Opencode)
- Migration: Nicht übernommen aus von "meinem" Code?
- Tests/Makefile(Workflow) nicht übernommen?
- Opencode "Vorteil": Extern ohne Abhängigkeit On-Prem entwickln mit Cloud Agnostic "Enforcement"
- Opencode Nutzung ADR?
- Drei verschiendene "root" apps? Operators, zwei Observability?
- Pipeline Out of Scope (z.B. für Scrape Configs)
