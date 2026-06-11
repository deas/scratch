## Alignment große technische Strukturen HADES

Ziel: Alignment Repos/Prozesse ("Slicing/Dicing")

### Format

Jeder 5-10 Minuten: Was/Wie/Warum (Golden Circle)
Vortragen/Schriftlich festhalten/übergeben (Schreiben ist Denken)
Output: Orientierung -> Speed/Stability

### Aspekte

- CD/Prozesse (Runners/Artefakte)
- Slice/Dice: Repos/Modules
- Eigenschaften Repos? Purpose? Primitiven?
- Testing (Pyramide)
- Speed/Stability
- Refactoring
- Observability/Feedback
- Constraints

### Design/Smaller Bits

- Docs (Wiki/Markdown/LLMs/Medienbruch)
- Observability
- Upstream Charts
- Kustomized Helm
- VMs
- AI
- OpenCode
- ArgoCD (Instanz Ownership)
- Stage Propagation
- Hetzner/GCA

## Random Personal Dumps

- Architektur Characteristik: Agility (Build for Change)
- -> Design / Kleinere Dinge folgen
- ~Eisberg~
- Conway's Law

## Golden Circle Testing

why: ... or it will happen (stability -> siehe auch speed)

- neue dev "stage"
- pipeline inline scripts
- kind in pipeline (vind)
- bats (shell scripts/chart)
- pytest
- Pyramide/module -> Repo structures
- kaos
- promtestlint (format)
- most common issues (IBM?)
- (sysdig)drift detection/monitoring (blackbox)
- value helmtest??
- test reports toolchain?
- bdd/tdd/generative/property
- kuttl (operator focus?)
- argocd-diff-preview

- zurück ziehen aus common operators?
- Sichtbarkeit branches
- Solution slopped by spec
- Cluster gar nicht sichtbar in git?
- Propagation prozess?
