# Install backend dependencies
install:
    cd backend && pip install -r requirements.txt
    cd client && npm install

# Initialize the database (create it if it doesn't exist)
init:
    cd backend && python -m app.db.init_db

# Drop the database (WARNING: This will delete all data!)
drop-db:
    cd backend && python -m app.db.drop_db

# Reset the database (drop, init, and populate)
reset-db:
    just drop-db
    just init
    just populate_db

# Generate a new Alembic migration with default message
generate-migration:
    cd backend && python -m app.db.generate_migration "Auto-generated migration"

# Apply Alembic migrations using config service for database connection
migrate:
    cd backend && python -m app.db.run_migrations

# Populate database with sample data
populate_db:
    cd backend && python -m app.db.populate_db

# Run the backend server
run-backend:
    cd backend && uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload

# Run the frontend client in development
run-client:
    cd client && npm start

# Build the frontend client for production
build-client:
    cd client && npm run build

# Preview the production build locally
preview-client:
    cd client && npm run preview -- --host 0.0.0.0

# Serve the production build with Python
serve-client-python:
    cd client/dist && python3 -m http.server 5173 --bind 0.0.0.0

# Serve the production build with npx serve
serve-client-node:
    npx serve -s client/dist -l 5173 -H 0.0.0.0

# Run both backend and frontend in development
run:
    just run-backend & just run-client

# Run backend with production client build
run-prod:
    just run-backend & just serve-client-python

# Test commands
test-backend:
    just clean-test-db
    cd backend && APP_ENV=test python -m pytest
    just clean-test-db

test-backend-unit:
    just clean-test-db
    cd backend && APP_ENV=test python -m pytest tests/unit/
    just clean-test-db

test-backend-integration:
    just clean-test-db
    cd backend && APP_ENV=test python -m pytest tests/integration/
    just clean-test-db

test-backend-coverage:
    just clean-test-db
    cd backend && APP_ENV=test python -m pytest --cov=app tests/
    just clean-test-db

test-backend-verbose:
    just clean-test-db
    cd backend && APP_ENV=test python -m pytest -v
    just clean-test-db

# Run specific backend test by grep pattern (e.g., just test-backend-grep "test_create_user")
test-backend-grep pattern:
    just clean-test-db
    cd backend && APP_ENV=test python -m pytest -k "{{pattern}}" -v
    just clean-test-db

# Run specific backend test file (e.g., just test-backend-file "tests/unit/test_auth.py")
test-backend-file file:
    just clean-test-db
    cd backend && APP_ENV=test python -m pytest "{{file}}" -v
    just clean-test-db

# Run backend tests by suite name (e.g., just test-backend-suite mcp, just test-backend-suite auth)
test-backend-suite suite:
    just clean-test-db
    cd backend && APP_ENV=test python -m pytest -k "{{suite}}" -v
    just clean-test-db

# List available backend test suites
list-backend-tests:
    #!/bin/bash
    echo "=== Backend Test Suites ==="
    echo "Available test suites (use with 'just test-backend-suite <suite>'):"
    echo ""

    # Extract test suite names from file names
    find backend/tests -name "test_*.py" -type f | while read file; do
        basename "$file" | sed 's/test_//' | sed 's/.py//'
    done | sort | while read suite; do
        echo "  $suite"
        # Show which files are included
        find backend/tests -name "*$suite*.py" -type f | sed 's|backend/tests/||' | sed 's/^/    - /'
        echo ""
    done

    echo "Examples:"
    echo "  just test-backend-suite mcp"
    echo "  just test-backend-suite auth"
    echo "  just test-backend-suite user"

# List available UI test suites
list-ui-tests:
    #!/bin/bash
    echo "=== UI Test Suites ==="
    echo "Available test suites (use with 'just test-ui-suite <suite>'):"
    echo ""

    # Extract test suite names from file names
    find client/tests -name "*.spec.ts" -type f | while read file; do
        basename "$file" | sed 's/.spec.ts//'
    done | sort | while read suite; do
        echo "  $suite"
        # Show which files are included
        find client/tests -name "*$suite*.spec.ts" -type f | sed 's|client/tests/||' | sed 's/^/    - /'
        echo ""
    done

    echo "Examples:"
    echo "  just test-ui-suite mcp"
    echo "  just test-ui-suite login"
    echo "  just test-ui-suite theme-toggle"

# Clean test database files
clean-test-db:
    rm -f backend/test.db backend/test_auth.db backend/test_database.db backend/*.db

# UI Test commands
# Run full UI test suite (starts backend+client, populates DB, runs tests)
test-ui:
    ./run-tests.sh

# Run specific UI test by grep pattern (e.g., just test-ui-grep "validation errors")
test-ui-grep pattern:
    #!/bin/bash
    ./run-tests.sh clean || true
    ./run-partial-tests.sh grep "{{pattern}}"

# Run specific UI test file (e.g., just test-ui-file "tests/mcp.spec.ts")
test-ui-file file:
    #!/bin/bash
    ./run-tests.sh clean || true
    ./run-partial-tests.sh file "{{file}}"

# Run specific UI test file with grep pattern (e.g., just test-ui-file-grep "tests/mcp.spec.ts" "should login")
test-ui-file-grep file pattern:
    #!/bin/bash
    ./run-tests.sh clean || true
    ./run-partial-tests.sh file-grep "{{file}}" "{{pattern}}"

# Run UI tests by suite name (e.g., just test-ui-suite mcp, just test-ui-suite login)
test-ui-suite suite:
    #!/bin/bash
    ./run-tests.sh clean || true
    ./run-partial-tests.sh suite "{{suite}}"

# Clean up test environment only (stops servers, removes test DB, cleans up)
test-ui-clean:
    ./run-tests.sh clean

# Client Unit Test commands (Jest)
# Run all client unit tests
test-client-unit:
    cd client && NODE_ENV=test npm test

# Run client unit tests with coverage
test-client-unit-coverage:
    cd client && NODE_ENV=test npm run test:coverage

# Run client unit tests in watch mode
test-client-unit-watch:
    cd client && NODE_ENV=test npm run test:watch

# Run specific client unit test file (e.g., just test-client-unit-file "api.test.ts")
test-client-unit-file file:
    cd client && NODE_ENV=test npm test -- "{{file}}"

# Run client unit tests matching pattern (e.g., just test-client-unit-grep "AuthContext")
test-client-unit-grep pattern:
    cd client && NODE_ENV=test npm test -- --testNamePattern="{{pattern}}"

# List available client unit test files
list-client-unit-tests:
    #!/bin/bash
    echo "=== Client Unit Test Files ==="
    echo "Available test files (use with 'just test-client-unit-file <file>'):"
    echo ""

    find client/src -name "*.test.ts" -o -name "*.test.tsx" | while read file; do
        basename "$file"
    done | sort | while read test_file; do
        echo "  $test_file"
        # Show the full path
        find client/src -name "$test_file" | sed 's|client/src/||' | sed 's/^/    - /'
        echo ""
    done

    echo "Examples:"
    echo "  just test-client-unit-file api.test.ts"
    echo "  just test-client-unit-file AuthContext.test.tsx"
    echo "  just test-client-unit-grep \"sign in\""

# Populate test database
populate-test-db:
    cd backend && APP_ENV=test python -m app.db.populate_test_db

# Clean up test database
cleanup-test-db:
    cd backend && APP_ENV=test python -m app.db.populate_test_db --cleanup

# SSH key management commands
ssh-use-germanilia:
    cp /tmp/host-germanilia-key ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa
    echo "Now using germanilia SSH key"
    ssh-add -l

ssh-use-iliagerman:
    cp /tmp/host-iliagerman-key ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa
    echo "Now using iliagerman SSH key"
    ssh-add -l

ssh-status:
    echo "Current SSH key fingerprint:"
    ssh-keygen -lf ~/.ssh/id_rsa
    echo "\nLoaded SSH keys:"
    ssh-add -l

git-test-connection:
    ssh -T git@github.com

# Create SQS queues in LocalStack
create_sqs:
    awslocal sqs create-queue --queue-name new-content
    awslocal sqs set-queue-attributes \
        --queue-url http://0.0.0.0:4566/000000000000/process-message-queue \
        --attributes '{ \
            "RedrivePolicy": "{\"deadLetterTargetArn\":\"arn:aws:sqs:us-east-1:000000000000:process-message-dead-letter-queue\",\"maxReceiveCount\":\"10\"}" \
        }'
    awslocal sqs set-queue-attributes \
        --queue-url http://0.0.0.0:4566/000000000000/new-content \
        --attributes '{ \
            "VisibilityTimeout": "10" \
        }'

# Purge all SQS queues in LocalStack
purge_sqs:
    awslocal sqs purge-queue --queue-url http://0.0.0.0:4566/000000000000/new-content --region=us-east-1

# Create Cognito User Pool and Client in AWS (only if they don't exist)
create_cognito:
    #!/bin/bash
    set -e

    # Change to backend directory to access configuration files
    cd backend

    # Load environment variables from .env file based on APP_ENV
    APP_ENV=${APP_ENV:-development}
    if [ -f ".env.$APP_ENV" ]; then
        export $(grep -v '^#' .env.$APP_ENV | xargs)
    fi

    # Load AWS credentials from secrets.yaml
    if [ -f "secrets.yaml" ]; then
        echo "Loading AWS credentials from secrets.yaml..."
        export AWS_ACCESS_KEY_ID=$(python3 -c "import yaml; data=yaml.safe_load(open('secrets.yaml')); print(data['aws']['access_key_id'])")
        export AWS_SECRET_ACCESS_KEY=$(python3 -c "import yaml; data=yaml.safe_load(open('secrets.yaml')); print(data['aws']['secret_access_key'])")
        export AWS_DEFAULT_REGION=$(python3 -c "import yaml; data=yaml.safe_load(open('secrets.yaml')); print(data['aws']['region'])")
        echo "✓ AWS credentials loaded successfully"
    else
        echo "Warning: secrets.yaml not found. Make sure AWS credentials are configured."
    fi

    # Use environment variables or defaults
    POOL_NAME=${COGNITO_POOL_NAME:-"MyAppUserPool"}
    CLIENT_NAME=${COGNITO_CLIENT_NAME:-"MyAppClient"}
    REGION=${COGNITO_REGION:-"us-east-1"}

    # Override AWS_DEFAULT_REGION with COGNITO_REGION if specified
    if [ -n "$COGNITO_REGION" ]; then
        export AWS_DEFAULT_REGION="$REGION"
        echo "Using Cognito region: $REGION"
    fi

    echo "Checking if Cognito User Pool exists in AWS..."

    # Try to find existing user pool by name
    EXISTING_POOL=$(aws cognito-idp list-user-pools --max-items 60 --region $REGION --query "UserPools[?Name=='$POOL_NAME'].Id" --output text 2>/dev/null || echo "")

    if [ -n "$EXISTING_POOL" ] && [ "$EXISTING_POOL" != "None" ]; then
        USER_POOL_ID="$EXISTING_POOL"
        echo "✓ User Pool already exists (ID: $USER_POOL_ID)"

        # Check if client exists
        EXISTING_CLIENT=$(aws cognito-idp list-user-pool-clients --user-pool-id "$USER_POOL_ID" --region $REGION --query "UserPoolClients[?ClientName=='$CLIENT_NAME'].ClientId" --output text 2>/dev/null || echo "")

        if [ -n "$EXISTING_CLIENT" ] && [ "$EXISTING_CLIENT" != "None" ]; then
            CLIENT_ID="$EXISTING_CLIENT"
            echo "✓ User Pool Client already exists (ID: $CLIENT_ID)"
            echo "Cognito resources are already set up!"
        else
            echo "User Pool exists but Client is missing. Creating Client..."
            # Create user pool client
            CLIENT_RESPONSE=$(aws cognito-idp create-user-pool-client \
                --user-pool-id "$USER_POOL_ID" \
                --client-name "$CLIENT_NAME" \
                --explicit-auth-flows "ALLOW_USER_PASSWORD_AUTH" "ALLOW_REFRESH_TOKEN_AUTH" "ALLOW_USER_SRP_AUTH" \
                --region $REGION \
                --query "UserPoolClient.ClientId" \
                --output text)
            CLIENT_ID="$CLIENT_RESPONSE"
            echo "✓ User Pool Client created successfully!"
        fi
    else
        echo "User Pool doesn't exist. Creating User Pool and Client..."

        # Create user pool with environment-specific configuration
        if [ "$APP_ENV" = "development" ]; then
            # Development: Simple setup, no email verification required
            echo "Creating development User Pool (no email verification)..."
            USER_POOL_RESPONSE=$(aws cognito-idp create-user-pool \
                --pool-name "$POOL_NAME" \
                --region $REGION \
                --policies '{"PasswordPolicy":{"MinimumLength":8,"RequireUppercase":false,"RequireLowercase":false,"RequireNumbers":false,"RequireSymbols":false}}' \
                --username-attributes email \
                --admin-create-user-config '{"AllowAdminCreateUserOnly":false}' \
                --query "UserPool.Id" \
                --output text)
        else
            # Production: Require email verification
            echo "Creating production User Pool (with email verification)..."
            USER_POOL_RESPONSE=$(aws cognito-idp create-user-pool \
                --pool-name "$POOL_NAME" \
                --region $REGION \
                --policies '{"PasswordPolicy":{"MinimumLength":8,"RequireUppercase":true,"RequireLowercase":true,"RequireNumbers":true,"RequireSymbols":false}}' \
                --username-attributes email \
                --admin-create-user-config '{"AllowAdminCreateUserOnly":false}' \
                --auto-verified-attributes email \
                --verification-message-template '{"DefaultEmailOption":"CONFIRM_WITH_CODE","EmailMessage":"Your verification code is {####}","EmailSubject":"Your verification code"}' \
                --query "UserPool.Id" \
                --output text)
        fi

        USER_POOL_ID="$USER_POOL_RESPONSE"
        echo "✓ User Pool created successfully! (ID: $USER_POOL_ID)"

        # Create user pool client
        CLIENT_RESPONSE=$(aws cognito-idp create-user-pool-client \
            --user-pool-id "$USER_POOL_ID" \
            --client-name "$CLIENT_NAME" \
            --explicit-auth-flows "ALLOW_USER_PASSWORD_AUTH" "ALLOW_REFRESH_TOKEN_AUTH" "ALLOW_USER_SRP_AUTH" \
            --region $REGION \
            --query "UserPoolClient.ClientId" \
            --output text)

        CLIENT_ID="$CLIENT_RESPONSE"
        echo "✓ User Pool Client created successfully!"
    fi

    echo ""
    echo "🎉 Cognito setup complete for environment: $APP_ENV"
    echo "User Pool Name: $POOL_NAME"
    echo "User Pool ID: $USER_POOL_ID"
    echo "Client Name: $CLIENT_NAME"
    echo "Client ID: $CLIENT_ID"
    echo "Region: $REGION"
    echo ""
    echo "💡 Note: This User Pool has minimal password requirements and no email verification for development ease."
    echo ""

    # Automatically add Cognito IDs to environment file
    echo "📝 Updating .env.$APP_ENV file..."
    if [ -f ".env.$APP_ENV" ]; then
        # Create a backup
        cp ".env.$APP_ENV" ".env.$APP_ENV.backup"

        # Remove any existing Cognito ID lines first (but keep COGNITO_REGION)
        grep -v "^COGNITO_USER_POOL_ID=" ".env.$APP_ENV" | grep -v "^COGNITO_CLIENT_ID=" | grep -v "^# Cognito IDs (from create_cognito" > ".env.$APP_ENV.tmp"
        mv ".env.$APP_ENV.tmp" ".env.$APP_ENV"

        # Add the new Cognito IDs
        echo "# Cognito IDs (from create_cognito_$APP_ENV output)" >> ".env.$APP_ENV"
        echo "COGNITO_USER_POOL_ID=$USER_POOL_ID" >> ".env.$APP_ENV"
        echo "COGNITO_CLIENT_ID=$CLIENT_ID" >> ".env.$APP_ENV"

        echo "✓ Added Cognito configuration to .env.$APP_ENV"
        echo "✓ Backup saved as .env.$APP_ENV.backup"
    else
        echo "⚠️  .env.$APP_ENV file not found. Please create it and add:"
        echo "COGNITO_USER_POOL_ID=$USER_POOL_ID"
        echo "COGNITO_CLIENT_ID=$CLIENT_ID"
        echo "COGNITO_REGION=$REGION"
    fi

    echo ""
    echo "🎉 Cognito setup complete! Your backend will automatically use the new configuration."

# Create Cognito for development environment
create_cognito_dev:
    APP_ENV=development just create_cognito

# Create Cognito for production environment
create_cognito_prod:
    APP_ENV=production just create_cognito

# Delete Cognito User Pool and Client
delete_cognito:
    #!/bin/bash
    set -e
    cd backend

    # Load environment variables
    APP_ENV=${APP_ENV:-development}
    if [ -f ".env.$APP_ENV" ]; then
        export $(grep -v '^#' .env.$APP_ENV | xargs)
    fi

    # Load AWS credentials from secrets.yaml
    if [ -f "secrets.yaml" ]; then
        echo "Loading AWS credentials from secrets.yaml..."
        export AWS_ACCESS_KEY_ID=$(python3 -c "import yaml; data=yaml.safe_load(open('secrets.yaml')); print(data['aws']['access_key_id'])")
        export AWS_SECRET_ACCESS_KEY=$(python3 -c "import yaml; data=yaml.safe_load(open('secrets.yaml')); print(data['aws']['secret_access_key'])")
        export AWS_DEFAULT_REGION=$(python3 -c "import yaml; data=yaml.safe_load(open('secrets.yaml')); print(data['aws']['region'])")
        echo "AWS credentials loaded successfully"
    fi

    # Get Cognito config from environment variables (not secrets.yaml)
    USER_POOL_ID=${COGNITO_USER_POOL_ID:-""}
    CLIENT_ID=${COGNITO_CLIENT_ID:-""}
    REGION=${COGNITO_REGION:-"us-east-1"}

    if [ -z "$USER_POOL_ID" ]; then
        echo "ERROR: COGNITO_USER_POOL_ID not found in environment variables"
        echo "Make sure .env.$APP_ENV contains COGNITO_USER_POOL_ID"
        exit 1
    fi

    echo "Deleting Cognito resources for environment: $APP_ENV"
    echo "User Pool ID: $USER_POOL_ID"
    echo "Client ID: $CLIENT_ID"
    echo "Region: $REGION"

    # Delete client if specified
    if [ -n "$CLIENT_ID" ]; then
        echo "Deleting User Pool Client: $CLIENT_ID"
        aws cognito-idp delete-user-pool-client --user-pool-id "$USER_POOL_ID" --client-id "$CLIENT_ID" --region "$REGION" || echo "Client deletion failed or already deleted"
    fi

    # Delete the user pool
    echo "Deleting User Pool: $USER_POOL_ID"
    aws cognito-idp delete-user-pool --user-pool-id "$USER_POOL_ID" --region "$REGION"

    # Remove Cognito IDs from environment file
    echo "Cleaning up environment variables..."
    if [ -f ".env.$APP_ENV" ]; then
        # Create a backup
        cp ".env.$APP_ENV" ".env.$APP_ENV.backup"

        # Remove the Cognito ID lines and related comments
        grep -v "^COGNITO_USER_POOL_ID=" ".env.$APP_ENV" | grep -v "^COGNITO_CLIENT_ID=" | grep -v "^# Cognito IDs (from create_cognito" > ".env.$APP_ENV.tmp"
        mv ".env.$APP_ENV.tmp" ".env.$APP_ENV"

        echo "Removed COGNITO_USER_POOL_ID and COGNITO_CLIENT_ID from .env.$APP_ENV"
        echo "Backup saved as .env.$APP_ENV.backup"
    fi

    echo "Cognito resources deleted successfully"

# Delete Cognito for development environment
delete_cognito_dev:
    APP_ENV=development just delete_cognito

# Delete Cognito for production environment
delete_cognito_prod:
    APP_ENV=production just delete_cognito

# Setup AWS services (LocalStack SQS + Real AWS Cognito)
setup_aws_services:
    just create_sqs
    just create_cognito

# Generate migration for Cognito fields
generate_cognito_migration:
    cd backend && python -m app.db.generate_cognito_migration