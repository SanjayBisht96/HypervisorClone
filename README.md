# Hypervisor-Clone

## System Design

### Overview
The system is designed to manage clusters, deployments, and scheduling tasks efficiently. It uses:
- **Django** for the backend API.
- **Celery** for task scheduling and asynchronous processing.
- **Redis** as the message broker for Celery.
- **Docker** to manage deployments and containerized services.

### Components
1. **Cluster Management**:
   - Create clusters with fixed resources (RAM, CPU, GPU).
   - Track available and allocated resources.

2. **Deployment Management**:
   - Create deployments for clusters using Docker images.
   - Allocate resources for deployments.
   - Queue deployments if resources are unavailable.

3. **Scheduling Algorithm**:
   - Prioritize deployments based on priority, resource utilization, and aging.
   - Maximize successful deployments.

4. **Task Processing**:
   - Use Celery to handle deployment scheduling and execution asynchronously.

---

### UML Diagram
Below is a high-level description of the UML diagram:

#### Apps:
1. **Cluster**:
   - Attributes: `name`, `ram`, `cpu`, `gpu`.
   - Relationships: One-to-Many with `Deployment`.

2. **Deployment**:
   - Attributes: `docker_image`, `ram_required`, `cpu_required`, `gpu_required`, `priority`, `status`.
   - Relationships: Belongs to `Cluster`.

3. **Scheduler**:
   - Handles deployment scheduling based on priority and resource availability.

#### Sequence:
1. User creates a cluster via the API.
2. User submits a deployment with priority(eg. 1,2,3 etc) request. Deployment is created and status is set to queued .
3. Users can trigger celery deployment scheduler by api or shell command.Scheduler checks resource availability and queues or executes the deployment.
4. Celery processes the deployment asynchronously.
5. Schedular priorities based on given priority and the created time of deployment and resource requirements of deployment. If created time is more than threshold and resource can be successfully allocated then the deployments priority is increased.

---

### Running the System with Docker

#### Prerequisites
- Install [Docker](https://www.docker.com/).
- Install [Docker Compose](https://docs.docker.com/compose/).

#### Steps to Run
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/Hypervisor-SimpliSmart.git
   cd Hypervisor-SimpliSmart

2. **Build the Docker Images**:
    ```bash
    docker build .
    docker-compose build
    ```

3. **Start the Services**:
    ```bash
    docker-compose up
    ```

4. **Running tests**:
```bash
   python -m venv venv
   .\venv\Scripts\Activate
   pip install -r requirements.txt
   pytest ./apps/tests/test_integration.py
   ```

**DB UML Diagram**:


User
| Column           | Type   | Notes             |
| ---------------- | ------ | ----------------- |
| id               | PK     | Primary key       |
| username         | string |                   |
| email            | string |                   |
| password         | string |                   |
| organization\_id | FK     | → Organization.id |


Organization
| Column      | Type     | Notes       |
| ----------- | -------- | ----------- |
| id          | PK       | Primary key |
| name        | string   |             |
| created\_at | datetime |             |


Cluster
| Column      | Type     | Notes       |
| ----------- | -------- | ----------- |
| id          | PK       | Primary key |
| name        | string   |             |
| ram         | integer  | In GB       |
| cpu         | integer  |             |
| gpu         | integer  |             |
| created\_at | datetime |             |



Deployment
| Column        | Type     | Notes               |
| ------------- | -------- | ------------------- |
| id            | PK       | Primary key         |
| cluster\_id   | FK       | → Cluster.id        |
| docker\_image | string   | Docker image name   |
| ram\_required | integer  | In GB               |
| cpu\_required | integer  |                     |
| gpu\_required | integer  |                     |
| priority      | integer  | Lower = higher pri. |
| status        | string   | E.g., pending, done |
| created\_at   | datetime |                     |


+-------------------+
|      User         |
+-------------------+
| id (PK)           |
| username          |
| email             |
| password          |
| organization_id   |
+-------------------+
         |
         | Foreign Key
         v
+-------------------+
|   Organization    |
+-------------------+
| id (PK)           |
| name              |
| created_at        |
+-------------------+

+-------------------+
|     Cluster       |
+-------------------+
| id (PK)           |
| name              |
| ram               |
| cpu               |
| gpu               |
| created_at        |
+-------------------+
         |
         | Foreign Key
         v
+-------------------+
|    Deployment     |
+-------------------+
| id (PK)           |
| cluster_id (FK)   |
| docker_image      |
| ram_required      |
| cpu_required      |
| gpu_required      |
| priority          |
| status            |
| created_at        |
+-------------------+