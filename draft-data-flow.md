sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant AI
    participant Validator
    participant Storage
    
    User->>Frontend: Enter WebToy description
    Frontend->>API: POST /api/generate (description)
    API->>AI: Generate code from description
    AI->>API: Return HTML/CSS/JS code
    
    API->>Validator: Validate & sanitize code
    Note over Validator: Check for malicious code<br/>Remove dangerous APIs<br/>Validate syntax
    
    alt Code passes validation
        Validator->>API: Return sanitized code
        API->>Storage: Store code with metadata
        Storage->>API: Return preview ID
        
        API->>Frontend: Return preview ID & sanitized code
        Frontend->>Frontend: Create sandboxed iframe
        Note over Frontend: Client-side sandboxing<br/>iframe + CSP headers
        
        Frontend->>User: Display preview
        
        User->>Frontend: Approve & publish
        Frontend->>API: POST /api/publish (previewId)
        
        API->>Storage: Update published status
        API->>Frontend: Return WebToy ID
        
        Frontend->>User: Display shareable link
        
        User->>User: Share link with others
        
    else Code fails validation
        Validator->>API: Return validation errors
        API->>Frontend: Return error details
        Frontend->>User: Display error & suggestions
    end
    
    Note over User,Storage: When shared link is visited
    
    User->>Frontend: Visit shared WebToy URL
    Frontend->>API: GET /toy/{webtoy_id}
    API->>Storage: Request WebToy code
    Storage->>API: Return WebToy code
    API->>User: Serve sandboxed WebToy HTML