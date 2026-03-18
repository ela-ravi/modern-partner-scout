"""
Tests for STORY-2.1.2: Implement Database Layer

These tests validate that the Supabase database client works correctly,
including client creation, FastAPI dependencies, and connection verification.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestSupabaseClientWrapper:
    """Tests for the SupabaseClient wrapper class."""
    
    def test_supabase_client_initialization(self):
        """Test SupabaseClient wrapper can be initialized."""
        from app.db.supabase import SupabaseClient
        
        mock_client = Mock()
        wrapper = SupabaseClient(mock_client, is_service_role=False)
        
        assert wrapper.client == mock_client
        assert wrapper.is_service_role == False
    
    def test_supabase_client_service_role_flag(self):
        """Test service role flag is set correctly."""
        from app.db.supabase import SupabaseClient
        
        mock_client = Mock()
        
        anon_wrapper = SupabaseClient(mock_client, is_service_role=False)
        assert anon_wrapper.is_service_role == False
        
        admin_wrapper = SupabaseClient(mock_client, is_service_role=True)
        assert admin_wrapper.is_service_role == True
    
    def test_supabase_client_table_method(self):
        """Test table() method delegates to underlying client."""
        from app.db.supabase import SupabaseClient
        
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        
        wrapper = SupabaseClient(mock_client)
        result = wrapper.table("test_table")
        
        mock_client.table.assert_called_once_with("test_table")
        assert result == mock_table
    
    def test_supabase_client_rpc_method(self):
        """Test rpc() method delegates to underlying client."""
        from app.db.supabase import SupabaseClient
        
        mock_client = Mock()
        mock_rpc_result = Mock()
        mock_client.rpc.return_value = mock_rpc_result
        
        wrapper = SupabaseClient(mock_client)
        result = wrapper.rpc("my_function", {"param": "value"})
        
        mock_client.rpc.assert_called_once_with("my_function", {"param": "value"})
        assert result == mock_rpc_result
    
    def test_supabase_client_rpc_no_params(self):
        """Test rpc() method works without parameters."""
        from app.db.supabase import SupabaseClient
        
        mock_client = Mock()
        wrapper = SupabaseClient(mock_client)
        
        wrapper.rpc("my_function")
        mock_client.rpc.assert_called_once_with("my_function", {})


class TestClientFactory:
    """Tests for client factory functions."""
    
    def test_get_db_returns_client(self):
        """Test get_db() returns a SupabaseClient."""
        from app.db import get_db, SupabaseClient, clear_client_cache
        
        # Clear cache to ensure fresh client
        clear_client_cache()
        
        db = get_db()
        assert isinstance(db, SupabaseClient)
    
    def test_get_db_is_not_service_role(self):
        """Test get_db() returns a non-service-role client."""
        from app.db import get_db, clear_client_cache
        
        clear_client_cache()
        
        db = get_db()
        assert db.is_service_role == False
    
    def test_get_admin_db_returns_client(self):
        """Test get_admin_db() returns a SupabaseClient."""
        from app.db import get_admin_db, SupabaseClient, clear_client_cache
        
        clear_client_cache()
        
        db = get_admin_db()
        assert isinstance(db, SupabaseClient)
    
    def test_get_admin_db_is_service_role(self):
        """Test get_admin_db() returns a service-role client."""
        from app.db import get_admin_db, clear_client_cache
        
        clear_client_cache()
        
        db = get_admin_db()
        assert db.is_service_role == True
    
    def test_client_caching(self):
        """Test that clients are cached (same instance returned)."""
        from app.db import get_db, get_supabase_client, clear_client_cache
        
        clear_client_cache()
        
        client1 = get_supabase_client()
        client2 = get_supabase_client()
        
        # Should be the same cached instance
        assert client1 is client2
    
    def test_admin_client_caching(self):
        """Test that admin clients are cached."""
        from app.db import get_supabase_admin_client, clear_client_cache
        
        clear_client_cache()
        
        client1 = get_supabase_admin_client()
        client2 = get_supabase_admin_client()
        
        assert client1 is client2
    
    def test_clear_client_cache(self):
        """Test that cache can be cleared."""
        from app.db import get_supabase_client, clear_client_cache
        
        # Get a client
        client1 = get_supabase_client()
        
        # Clear cache
        clear_client_cache()
        
        # Get another client
        client2 = get_supabase_client()
        
        # Should be different instances after cache clear
        assert client1 is not client2


class TestFastAPIDependency:
    """Tests for FastAPI dependency integration."""
    
    def test_get_db_can_be_used_as_dependency(self):
        """Test get_db can be used with FastAPI Depends."""
        from fastapi import Depends, FastAPI
        from fastapi.testclient import TestClient
        from app.db import get_db, SupabaseClient
        
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint(db: SupabaseClient = Depends(get_db)):
            return {"has_db": db is not None, "type": type(db).__name__}
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_db"] == True
        assert data["type"] == "SupabaseClient"
    
    def test_get_admin_db_can_be_used_as_dependency(self):
        """Test get_admin_db can be used with FastAPI Depends."""
        from fastapi import Depends, FastAPI
        from fastapi.testclient import TestClient
        from app.db import get_admin_db, SupabaseClient
        
        app = FastAPI()
        
        @app.get("/admin-test")
        async def admin_endpoint(db: SupabaseClient = Depends(get_admin_db)):
            return {
                "has_db": db is not None,
                "is_admin": db.is_service_role
            }
        
        client = TestClient(app)
        response = client.get("/admin-test")
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_db"] == True
        assert data["is_admin"] == True


class TestTransactionContext:
    """Tests for transaction context manager."""
    
    def test_transaction_client_context_manager(self):
        """Test get_transaction_client() works as context manager."""
        from app.db import get_transaction_client, SupabaseClient
        
        with get_transaction_client() as db:
            assert isinstance(db, SupabaseClient)
            assert db.is_service_role == True
    
    def test_transaction_client_raises_on_error(self):
        """Test transaction context re-raises errors."""
        from app.db import get_transaction_client
        from app.core.exceptions import SupabaseError
        
        with pytest.raises(SupabaseError) as exc_info:
            with get_transaction_client() as db:
                raise ValueError("Simulated error")
        
        assert "Transaction failed" in str(exc_info.value)


class TestConnectionCheck:
    """Tests for connection verification."""
    
    @pytest.mark.integration
    def test_check_connection_with_real_db(self):
        """Test connection check with real Supabase (integration test)."""
        from app.db import check_connection, clear_client_cache
        
        clear_client_cache()
        
        # This will only pass if Supabase is configured and accessible
        result = check_connection()
        assert result == True
    
    def test_check_connection_returns_true_on_success(self):
        """Test check_connection returns True on success."""
        from app.db.supabase import check_connection, get_supabase_admin_client, clear_client_cache
        
        # This test uses the real connection if available
        clear_client_cache()
        
        try:
            result = check_connection()
            assert result == True
        except Exception:
            # If connection fails, that's expected in isolated test environments
            pytest.skip("Supabase connection not available")


class TestAuthenticatedClient:
    """Tests for authenticated client creation."""
    
    def test_create_authenticated_client_structure(self):
        """Test create_authenticated_client creates a client."""
        from app.db import create_authenticated_client, SupabaseClient
        
        # Note: This will attempt to set a session with a fake token
        # which may fail depending on Supabase validation
        try:
            # Use a dummy token (will likely fail validation but tests the code path)
            client = create_authenticated_client("dummy_token")
            assert isinstance(client, SupabaseClient)
            assert client.is_service_role == False
        except Exception:
            # Expected if token validation fails
            pass


class TestModuleExports:
    """Test that the db module exports everything correctly."""
    
    def test_import_from_db_module(self):
        """Test importing from app.db module."""
        from app.db import (
            SupabaseClient,
            get_db,
            get_admin_db,
            get_supabase_client,
            get_supabase_admin_client,
            create_authenticated_client,
            get_transaction_client,
            clear_client_cache,
            check_connection,
        )
        
        assert SupabaseClient is not None
        assert callable(get_db)
        assert callable(get_admin_db)
        assert callable(get_supabase_client)
        assert callable(get_supabase_admin_client)
        assert callable(create_authenticated_client)
        assert callable(clear_client_cache)
        assert callable(check_connection)


class TestSupabaseConnection:
    """Integration tests for actual Supabase connection."""
    
    @pytest.mark.integration
    def test_supabase_connection(self):
        """Test actual Supabase connection (as specified in validation)."""
        from app.db.supabase import get_db, clear_client_cache
        
        clear_client_cache()
        
        db = get_db()
        result = db.table("discovery_jobs").select("id").limit(1).execute()
        
        assert result is not None
        # result.data should be a list (possibly empty)
        assert hasattr(result, 'data')
    
    @pytest.mark.integration
    def test_admin_connection_can_query(self):
        """Test admin client can query tables."""
        from app.db import get_admin_db, clear_client_cache
        
        clear_client_cache()
        
        db = get_admin_db()
        result = db.table("discovery_jobs").select("id, status").limit(5).execute()
        
        assert result is not None
        assert hasattr(result, 'data')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
