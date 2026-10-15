# HR Genie: how it works

A plain primer for a cold-starting session or human. Source of truth for
detail: the Confluence tree (overview page 2862809419) and
projects/hr-genie.md; the diagram source
architecture/system-map.mmd is canonical for topology. This primer walks the
system in prose; assertions carry absolute dates. Written 2026-10-11; the
44-asset wave (BSYS-29498) sits in Final Tech Review as of this date.

## What it is

HR Genie is a Slack-first employee self-service agent for Workday HR
questions and actions. An employee DMs the genie; it answers from Workday
data, executes self-service actions (time off, profile changes, pay and
benefits lookups), files Jira tickets when a request needs a human, and a
separate platform watches HR business processes and proactively notifies
employees. All of it runs in the Workato dev workspace (ws 3535597) until
promotion; real employee absence data arrives at prod promotion because dev
is tenant-limited (Workday impl tenant wd108 vs PROD).

## The four moving parts

1. **The genie** (gin-AYbxpMha-YenKAJ-CD) is the Slack front door. It owns
   the conversation: employee DMs in, answers out, JSM ticket creation on
   human-needed requests.
2. **Skills** are the genie's hands, each a Workato recipe calling Workday
   as the END USER via the Workday End-User MCP (VUA): check business
   process status (82778233), the FTO gate pair (82839617 + 82862012),
   submit time off (78622059). Skills attach to the genie as tools.
3. **The proactive notification platform** watches Workday and speaks
   first: inbox-task approvals, PTO events, anniversaries, the BP
   completion notification family (BSYS-28313). Its messenger choke point
   is recipe 74094657; it triggers the genie's conversations via a
   chat trigger (ginct-AbbxJxmX-gchtnT-CD) so proactive messages open into
   real dialogue.
4. **The intelligence platform** is the telemetry loop: conversation
   events flow in from the Agent Studio events API (90-day purge), get
   collected, judged, rolled up, and digested; an Analyst Genie queries
   them and dashboards render them.

## How an employee message flows

Employee DMs the genie in Slack. The genie classifies the request: answerable
self-service (a skill runs against Workday as the user), needs a human (a
JSM ticket is created), or conversational. Every conversation event lands in
the intelligence ledgers afterward. Notifications go the other direction:
Workday crons feed the notification platform, which DMs the employee and
hands the thread to the genie.

## The odd duck: Consumer Endpoints

The OOO status API (BTSUP-72246) is not genie-shaped: it is an HTTP GET
surface (v1/ooo-status, Api-Token) consumed by Team UI Engineering
Utilities recipes (Vlad Sharikov). Its roster comes from the #team-ui Slack
channel via a workspace-owned bot (BT Consumer Endpoints A0C6Y8E5U3C, never
end-user creds); its leave snapshots come from Workday WQL
(timeOffByDateTaken, allWorkers.onLeave). Absence accuracy for PROD arrives
only at prod promotion (see the tenant limit above).

## Storage

Workato data tables hold the notification and telemetry ledgers
(155278, 132894, 156842, 156841 and siblings). They are append-heavy event
stores; rollups and digests read them.

## Where the bodies are buried (traps with their own docs)

- VUA revert on push: domains/vua-revert-on-push.md (canonical).
- Orca browser runs on the AHQ Production workspace and cannot open dev
  recipes; dev UI work needs the dev workspace URL.
- ruby() formula whitelist bans .map blocks; use custom-code steps.

## Reading order for a new session

1. This primer. 2. architecture/system-map.mmd (canonical topology, every
node line-cited). 3. projects/hr-genie.md hub for the live build state.
4. The per-ticket plan files here for anything in flight.
