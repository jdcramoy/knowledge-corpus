# KB digest — project-dreamer — 2026-10-27

## Change surface (nightly sync)
- docs: 9 docs changed
- blog: 88 docs changed
- changelog: 10 docs changed
- inspiration: 19 docs changed
- eip: 103 docs changed
- claude: 663 docs changed
- temporal: 10 docs changed
- n8n: 1361 docs changed
- prefect: 329 docs changed
- restate: 213 docs changed
- mcp: 357 docs changed
- slack: 3227 docs changed
- snowflake: 9184 docs changed
- dbt: 9 docs changed
- trigger: 30 docs changed
- hf-hub: 3 docs changed
- secondary corpora (non-Workato): 15386 docs changed (excluded from the quiet-night floor)
- DELTA 229 workato-owned changed docs (> 50 floor) — this night is NOT quiet regardless of lens results

## Lens queries (live retrieval)

### capability for projects
_query: `new connector capability feature` (source: docs) — confidence 3.559 bits_
1. [docs] Workato connectors - RPA by Workato
   https://docs.workato.com/en/connectors/rpa-by-workato.md
   ### Complete setup in Workato  Complete the following steps to configure the connection to RPA by Workato:  1. Click **Create > Connection** or press C twice.     2. Search for and select `RPA by Work...
2. [docs] UiPath
   https://docs.workato.com/en/connectors/uipath.md
    # UiPath  [UiPath](https://www.uipath.com/) combines core Robotic Process Automation (RPA) capabilities with tools for process discovery and analytics, making it easy to automate thousands of workflo...
3. [docs] Community connectors
   https://docs.workato.com/en/developing-connectors/community/community.md
   ## Community recipe FAQs  Do I receive updates when the community connector is updated by the connector developer?  Connectors installed from the community library always retain a relationship with th...
4. [docs] Configure Gong as a data pipeline source
   https://docs.workato.com/en/data-orchestration/data-pipeline-recipe/configure-gong.md
   ## Features supported  The following features are supported when you use Gong as a pipeline source:  - **Cloud connectivity**: Connects to the Gong API v2 over https using a customer-specific, region-...
5. [docs] Workato connectors - LaunchDarkly
   https://docs.workato.com/en/connectors/launchdarkly.md
   ### Get record details by ID  The get record action supports **Feature Flag**, **Feature Flag Status**, **Flag Setting for User**, **Project**, and **User**.  > **INFO** >  > The get feature flag stat...
6. [docs] Enterprise Context by Workato
   https://docs.workato.com/en/connectors/enterprise-context-by-workato.md
    # Enterprise Context by Workato  The Enterprise Context by Workato connector gives builders a recipe-native way to manage the documents inside a Workato [knowledge base](/en/agentic/agent-studio/know...
7. [docs] Version a connector
   https://docs.workato.com/en/ahq-shared-connector-version.md
    # Version a connector  If you have a new version of a shared connector, you can change it very easily in Automation HQ.  > **Prerequisite** >  > You must first develop, test, and deploy a [connectors...
8. [docs] Workato connectors - Stripe - New object event trigger
   https://docs.workato.com/en/connectors/stripe/new-object-event-trigger.md
    # Stripe - New object event trigger (real-time)  This trigger checks for new events related to specified objects in Stripe, in real time. Supported objects are:  - Account - Application fee - Capabil...
9. [docs] Lookup tables by Workato
   https://docs.workato.com/en/features/lookup-tables.md
    # Lookup tables  Lookup tables enable recipes to efficiently store, reference, and manage frequently used data using a table of entry rows and value columns, similar to a cross-reference table.  The ...
10. [docs] Workato connectors - SAP RFC
   https://docs.workato.com/en/connectors/sap.md
   ## Additional capabilities  The SAP RFC connector supports the following capabilities:  - Direct connection to SAP, allowing you to establish a connection to the application server. - Message server c...
11. [docs] Using the Workato Connector SDK
   https://docs.workato.com/en/developing-connectors/sdk/quickstart/quickstart.md
   ### Create a new custom connector  You can create a new custom connector from the Connector SDK main screen.  In the top right corner of the page, you'll see a button to create a new custom connector....
12. [docs] Connector Copilot
   https://docs.workato.com/en/developing-connectors/sdk/copilot.md
    # Workato Connector Copilot  The Workato Connector Copilot uses Large Language Models (LLMs) to enhance and accelerate your connector-building experience. This enables you to develop connectors quick...

### architecture inspiration
_query: `architecture pattern design principle` (source: github) — confidence 3.576 bits_
1. [github] Architecture and Design Patterns
   https://github.com/nilbuild/developer-roadmap/blob/HEAD/roadmaps/android/content/design--architecture@jePGzTejFe4ryA5qFFmjl.md
   # Architecture and Design Patterns  **Design Architecture** refers to structuring the code in a way that increases its readability, maintainability, and testability. There are several ways to design a...
2. [github] Architectural Design Principles
   https://github.com/mehdihadeli/awesome-software-architecture/blob/HEAD/docs/software-architecture/principles/architectural-design-principles.md
   ## 📘 Resources - [chanakaudaya/solution-architecture-patterns](https://github.com/chanakaudaya/solution-architecture-patterns) - Reusable, vendor-neutral, industry-specific, vendor-specific solution a...
3. [github] Patterns and design principles
   https://github.com/nilbuild/developer-roadmap/blob/HEAD/roadmaps/software-architect/content/patterns--design-principles@_U0VoTkqM1d6NR13p5azS.md
   # Patterns and design principles  In the realm of software architecture, patterns and design principles are foundational tools that enable architects to create robust, scalable, and maintainable syste...
4. [github] Architectural Principles
   https://github.com/nilbuild/developer-roadmap/blob/HEAD/roadmaps/software-design-architecture/content/architectural-principles@XBCxWdpvQyK2iIG2eEA1K.md
   # Architectural Principles  Architectural principles refer to a set of guidelines or rules that are used to guide the design and development of a software architecture. These principles are intended t...
5. [github] Architectural Patterns
   https://github.com/nilbuild/developer-roadmap/blob/HEAD/roadmaps/software-design-architecture/content/architectural-patterns@jq916t7svaMw5sFOcqZSi.md
   # Architectural Patterns  Architectural patterns are reusable solutions to common problems encountered during the high-level design of software systems. They provide a structural template that defines...
6. [github] Architectural Patterns
   https://github.com/nilbuild/developer-roadmap/blob/HEAD/roadmaps/computer-science/content/architectural-patterns@BGhJNtszbYJtKyhqr2jax.md
   # Architectural Patterns  Architectural patterns are a high-level design pattern that focuses on the overall structure of the system. They are similar to design patterns, but they are more concerned w...
7. [github] State Design Pattern
   https://github.com/mehdihadeli/awesome-software-architecture/blob/HEAD/docs/software-architecture/architecture-patterns/design-patterns/state-pattern.md
   # State Design Pattern  ### 📕Articles - [SOLID Wash Tunnel - State](https://www.ledjonbehluli.com/posts/wash-tunnel/state/)...
8. [github] Architectural Patterns
   https://github.com/nilbuild/developer-roadmap/blob/HEAD/roadmaps/backend/content/architectural-patterns@tHiUpG9LN35E5RaHddMv5.md
   # Architectural Patterns  Architectural patterns are reusable solutions to common software architecture problems. They address issues like performance limitations, high availability, and business risk...
9. [github] Architectural Patterns
   https://github.com/nilbuild/developer-roadmap/blob/HEAD/roadmaps/software-design-architecture/content/architectural-patterns@gJYff_qD6XS3dg3I-jJFK.md
   # Architectural Patterns  Architectural patterns are high-level structural templates that shape the overall organization of a system, such as layered architecture, microservices, event-driven, and ser...
10. [github] Architectural Styles
   https://github.com/nilbuild/developer-roadmap/blob/HEAD/roadmaps/computer-science/content/architectural-styles@X1wv7xV69IEzepg8bF8oZ.md
   # Architectural Styles  Architectural patterns are the fundamental organization of a system, defining how the system is composed and how its components interact. Architectural patterns are identified ...
11. [github] Design Principles
   https://github.com/nilbuild/developer-roadmap/blob/HEAD/roadmaps/software-design-architecture/content/design-principles@p96fNXv0Z4rEEXJR9hAYX.md
   # Design Principles  Design principles are fundamental guidelines that help software engineers create systems that are maintainable, scalable, robust, and easy to understand. They represent best pract...
12. [github] Architectural Styles
   https://github.com/nilbuild/developer-roadmap/blob/HEAD/roadmaps/software-design-architecture/content/architectural-styles@En_hvwRvY6k_itsNCQBYE.md
   # Architectural Styles  Architectural styles are high-level patterns that define the fundamental structure and organization of a software system. They provide a standardized way to arrange components,...

## Your job
Opinion: do new capabilities map to active projects' next milestones?
Read the hits, form an OPINION (1-3 lines: how does this relate to ongoing work / your domain?), post it to your gossip-bus outbox. Do NOT file proposals — that is the dreamer's synthesis job.
