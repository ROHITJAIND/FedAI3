# Architecture Decision Records (ADRs)

## ADR-001: Federated Learning Algorithm Selection

**Status:** Accepted  
**Date:** 2024-12-28  
**Context:** Need to choose federated learning algorithm for medical image classification

### Decision
We will implement the Federated Averaging (FedAvg) algorithm as our core federated learning approach.

### Rationale
- **Proven Effectiveness**: FedAvg is well-established in federated learning research
- **Medical Domain Suitability**: Works well with image classification tasks
- **Implementation Simplicity**: Straightforward to implement and debug
- **Hospital Compatibility**: Minimal computational overhead for hospital clients

### Alternatives Considered
- **FedProx**: More complex, better for heterogeneous data but harder to implement
- **FedNova**: Addresses client drift but requires more sophisticated coordination
- **Custom Algorithm**: Too risky for initial implementation

### Consequences
- Simple weighted averaging of model parameters
- May struggle with highly heterogeneous hospital data
- Future migration to more advanced algorithms possible

---

## ADR-002: Model Architecture for Fetal Position Classification

**Status:** Accepted  
**Date:** 2024-12-28  
**Context:** Need to select CNN architecture for medical image classification

### Decision
We will use ResNet-18 as the base architecture with transfer learning from ImageNet.

### Rationale
- **Medical Imaging Proven**: ResNet architectures work well for medical images
- **Computational Efficiency**: ResNet-18 is lightweight enough for hospital deployment
- **Transfer Learning**: Pre-trained weights provide good starting point
- **Federated Learning Compatible**: Parameter structure works well with FedAvg

### Alternatives Considered
- **Custom CNN**: Too much development time, uncertain performance
- **Vision Transformer**: Too computationally expensive for hospital environments
- **ResNet-50/101**: Too large for federated learning parameter transmission

### Consequences
- Good balance of accuracy and computational efficiency
- May need fine-tuning for specific ultrasound image characteristics
- Easy to replace with other architectures if needed

---

## ADR-003: Communication Protocol for Federated Learning

**Status:** Accepted  
**Date:** 2024-12-28  
**Context:** Need secure, reliable communication between hospitals and central server

### Decision
We will use HTTPS with JSON payloads for model parameter transmission.

### Rationale
- **Healthcare Compatibility**: HTTPS is standard in healthcare IT environments
- **Firewall Friendly**: Port 443 is typically open in hospital networks
- **JSON Simplicity**: Easy to serialize/deserialize model parameters
- **Debugging**: Human-readable format aids in troubleshooting

### Alternatives Considered
- **gRPC**: More efficient but complex, may face firewall issues
- **Custom Binary Protocol**: Efficient but harder to debug and maintain
- **Message Queues**: Adds infrastructure complexity

### Consequences
- Slightly higher bandwidth usage than binary protocols
- Easy integration with existing hospital IT infrastructure
- Standard security practices apply

---

## ADR-004: Data Storage and Privacy Architecture

**Status:** Accepted  
**Date:** 2024-12-28  
**Context:** Must ensure patient data never leaves hospital premises

### Decision
We will implement a "data never leaves hospital" architecture with local-only storage.

### Rationale
- **HIPAA Compliance**: Eliminates most privacy concerns
- **Hospital Trust**: Easier to gain hospital participation
- **Regulatory Simplicity**: Reduces compliance burden
- **Technical Clarity**: Clear separation of data and model parameters

### Architecture Components
- Local data storage at each hospital
- Model parameter-only transmission
- Encrypted parameter storage
- Comprehensive audit logging

### Consequences
- Cannot perform centralized data analysis
- Debugging requires hospital-specific investigation
- Strong privacy guarantees build trust

---

## ADR-005: Web Interface Technology Stack

**Status:** Accepted  
**Date:** 2024-12-28  
**Context:** Need user-friendly interface for hospital administrators

### Decision
We will use Flask with server-side rendering and minimal JavaScript.

### Rationale
- **Python Integration**: Seamless integration with ML codebase
- **Hospital IT Friendly**: Simple deployment, minimal client-side requirements
- **Security**: Server-side rendering reduces attack surface
- **Maintenance**: Single technology stack reduces complexity

### Features
- Real-time training dashboards
- Patient report generation
- System health monitoring
- Data upload interfaces

### Alternatives Considered
- **React/Vue SPA**: More complex deployment, requires Node.js
- **Django**: Heavier framework, unnecessary features
- **Pure API**: Would require separate frontend development

### Consequences
- Simpler deployment and maintenance
- May need JavaScript for real-time updates
- Easy to enhance with modern frontend later

---

## ADR-006: Model Evaluation and Validation Strategy

**Status:** Accepted  
**Date:** 2024-12-28  
**Context:** Need comprehensive evaluation of federated vs. centralized learning

### Decision
We will implement dual evaluation comparing local, global, and centralized models.

### Evaluation Components
- **Local Model Performance**: Each hospital's model on local test data
- **Global Model Performance**: Federated model on each hospital's test data
- **Centralized Baseline**: Traditional model trained on combined data (for research)
- **Cross-Hospital Generalization**: Global model on other hospitals' data

### Metrics
- Classification accuracy, precision, recall, F1-score
- Confusion matrices for clinical interpretation
- Training convergence analysis
- Communication efficiency metrics

### Rationale
- **Clinical Validation**: Doctors need confidence in AI recommendations
- **Research Value**: Demonstrates federated learning effectiveness
- **Continuous Improvement**: Identifies areas for model enhancement
- **Regulatory Support**: Comprehensive evaluation supports approval processes

### Consequences
- More complex evaluation pipeline
- Valuable insights for federated learning research
- Strong foundation for clinical adoption

---

## ADR-007: Deployment and Scalability Architecture

**Status:** Accepted  
**Date:** 2024-12-28  
**Context:** System must scale from 3 to 50+ hospitals

### Decision
We will use containerized deployment with Docker and support both synchronous and asynchronous federated learning.

### Deployment Strategy
- **Docker Containers**: Easy deployment across different hospital environments
- **Configuration Management**: Environment-specific settings
- **Health Monitoring**: Automated system health checks
- **Graceful Scaling**: Dynamic client addition/removal

### Federated Learning Modes
- **Synchronous**: All hospitals train simultaneously (better convergence)
- **Asynchronous**: Hospitals train independently (better availability)
- **Hybrid**: Adaptive mode based on hospital participation

### Rationale
- **Hospital IT Compatibility**: Docker is widely supported
- **Operational Flexibility**: Hospitals can join/leave without system disruption
- **Performance Optimization**: Different modes for different scenarios
- **Future-Proofing**: Architecture supports significant growth

### Consequences
- More complex coordination logic
- Better real-world deployment characteristics
- Supports diverse hospital operational patterns

These architectural decisions guided our implementation approach, ensuring we built a system that meets both technical requirements and real-world healthcare deployment needs.