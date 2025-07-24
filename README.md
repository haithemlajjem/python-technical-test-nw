# Python Technical Test

This project is a FastAPI web service for managing **Sites** and **Groups**. Sites represent energy installations, and Groups help organize them. The app supports full CRUD operations, applies some business rules, and is designed to handle country-specific fields, making it easy to extend in the future.

---

## Features

### Models
- **Site**
  - Supports country-specific fields (`useful_energy_at_1_megawatt` for France, `efficiency` for Italy).
  - Includes power capacities and installation metadata.
- **Group**
  - Can include multiple Sites or other Groups.
  - Includes type classification (`group1`, `group2`, `group3`).

### Relationships
- Many-to-Many: Sites ↔ Groups  
- Hierarchical: Groups ↔ Child Groups

---

## 🔧 Business Rules

| Rule | Description |
|------|-------------|
| France | Only **one** French site can be installed **per day** |
| Italy  | Italian sites **must be installed on weekends** |
| Group3 Restriction | Sites **cannot** be associated with groups of type **group3** |

---

## API Endpoints

### 🔹 Sites
- `GET /sites` – List with filtering (`country`) & sorting (`installation_date`, etc.)
- `POST /sites` – Create site with validations
- `PATCH /sites/{site_id}` – Update site
- `DELETE /sites/{site_id}` – Delete site

### 🔹 Groups
- `GET /groups` – List groups with filters
- `POST /groups` – Create a group
- `PATCH /groups/{group_id}` – Update group
- `DELETE /groups/{group_id}` – Delete group
- `POST /groups/{group_id}/child-groups` – Add nested group
- `DELETE /groups/{group_id}/child-groups` – Remove nested group

---

## Testing

- To run tests:

```bash
poetry run pytest
