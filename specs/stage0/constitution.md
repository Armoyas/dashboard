# Constitution

> Reference Repository: Armoyas/analytical-dashboard
> New Repository: Armoyas/dashboard

## 1. Purpose

This project implements a dashboard application using Spec-Driven Development (SDD). It is built upon the reference architecture established in the Armoyas/analytical-dashboard repository, with an explicit focus on specification-first development.

## 2. Scope

### In Scope

1. **Dashboard Application**
   - FastAPI backend API providing analytics data
   - Next.js frontend with React components
   - DuckDB database with ZarrinPal analytics schema
   - Nginx reverse proxy for routing

2. **Specification Artifacts**
   - Stage 0 project definition and architecture specs
   - Future stage specifications for detailed development
   - API contract documentation
   - Deployment and configuration guides

3. **Deployment**
   - Docker Compose-based deployment
   - Nginx reverse proxy configuration
   - Integration with existing ZarrinPal analytics schema

### Out of Scope

1. **Production Infrastructure Management**
   - Server provisioning
   - SSL certificate management
   - Database administration beyond the dashboard

2. **Business Intelligence Features**
   - Advanced analytics modeling
   - Machine learning pipelines
   - Predictive analytics

3. **Authentication & Authorization**
   - User management systems
   - Role-based access control
   - SSO integration

## 3. Stakeholders

| Role | Name | Responsibilities |
|------|------|-----------------|
| Product Owner | Armoyas | Define dashboard requirements and acceptance criteria |
| Lead Developer | Armoyas | Implement the dashboard application following SDD methodology |
| DevOps Engineer | Armoyas | Configure deployment environment (Docker, Nginx) |

## 4. Principles

1. **Spec-First Development**: All features must be defined in specifications before implementation.
2. **Reference Architecture Compliance**: Follow patterns established in Armoyas/analytical-dashboard.
3. **ZarrinPal Schema Compatibility**: Maintain compatibility with the merchant_key, session_status, amount schema.
4. **Null-Safety**: All code must handle null/undefined values gracefully.
5. **Docker-First**: All development and deployment must be containerized.
6. **Version Pinning**: Major versions (Next.js, FastAPI) must be explicitly pinned.

## 5. Success Criteria

1. Dashboard application deployed successfully with Docker Compose
2. API endpoints documented with OpenAPI specification
3. Frontend renders analytics data correctly
4. Nginx routing configured for both API and frontend
5. Stage 0 specifications reviewed and approved
6. All files committed to GitHub repository Armoyas/dashboard

## 6. Definitions

| Term | Definition |
|------|-----------|
| SDD | Spec-Driven Development - a methodology where all features are defined in specifications before implementation |
| Stage 0 | Initial specification stage defining project identity, architecture, and high-level design |
| ZarrinPal Schema | Data model for payment analytics with merchant_key, session_status, amount (Rials), and adjusted_fee fields |
| Reference Repo | Armoyas/analytical-dashboard - the existing repository used as architectural reference |
| Merchant Key | Unique identifier for a ZarrinPal merchant account |
| Session Status | Status of a payment session (e.g., completed, failed, pending) |
