"""
测试 yai_nexus_api_middleware.responses 模块的单元测试。
"""
import pytest
from unittest.mock import patch
from yai_nexus_api_middleware.responses import ApiResponse


class TestApiResponse:
    """测试 ApiResponse 模型的功能"""

    @patch("yai_nexus_api_middleware.responses.trace_context.get_trace_id")
    def test_成功响应创建_无数据(self, mock_trace_id):
        """测试创建无数据的成功响应"""
        mock_trace_id.return_value = "test_trace_123"
        
        response = ApiResponse.success()
        
        assert response.code == "0"
        assert response.message == "操作成功"
        assert response.data is None
        assert response.trace_id == "test_trace_123"

    @patch("yai_nexus_api_middleware.responses.trace_context.get_trace_id")
    def test_成功响应创建_带数据(self, mock_trace_id):
        """测试创建带数据的成功响应"""
        mock_trace_id.return_value = "test_trace_456"
        test_data = {"key": "value", "number": 42}
        
        response = ApiResponse.success(data=test_data)
        
        assert response.code == "0"
        assert response.message == "操作成功"
        assert response.data == test_data
        assert response.trace_id == "test_trace_456"

    @patch("yai_nexus_api_middleware.responses.trace_context.get_trace_id")
    def test_失败响应创建_无数据(self, mock_trace_id):
        """测试创建无数据的失败响应"""
        mock_trace_id.return_value = "test_trace_789"
        
        response = ApiResponse.failure(code="ERR_001", message="操作失败")
        
        assert response.code == "ERR_001"
        assert response.message == "操作失败"
        assert response.data is None
        assert response.trace_id == "test_trace_789"

    @patch("yai_nexus_api_middleware.responses.trace_context.get_trace_id")
    def test_失败响应创建_带数据(self, mock_trace_id):
        """测试创建带数据的失败响应"""
        mock_trace_id.return_value = "test_trace_abc"
        error_data = {"error_details": "详细错误信息"}
        
        response = ApiResponse.failure(
            code="ERR_002", 
            message="参数错误", 
            data=error_data
        )
        
        assert response.code == "ERR_002"
        assert response.message == "参数错误"
        assert response.data == error_data
        assert response.trace_id == "test_trace_abc"

    def test_失败响应创建_错误代码为零(self):
        """测试创建失败响应时代码不能为'0'"""
        with pytest.raises(ValueError, match="错误响应的代码不能为 '0'"):
            ApiResponse.failure(code="0", message="不应该成功")

    @patch("yai_nexus_api_middleware.responses.trace_context.get_trace_id")
    def test_响应转换为字典(self, mock_trace_id):
        """测试响应对象转换为字典"""
        mock_trace_id.return_value = "test_trace_dict"
        test_data = {"test": "data"}
        
        response = ApiResponse.success(data=test_data)
        response_dict = response.model_dump()
        
        expected = {
            "code": "0",
            "message": "操作成功",
            "data": test_data,
            "trace_id": "test_trace_dict"
        }
        assert response_dict == expected

    def test_响应从字典创建(self):
        """测试从字典创建响应对象"""
        data = {
            "code": "TEST_001",
            "message": "测试消息",
            "data": {"test": "value"},
            "trace_id": "manual_trace_id"
        }
        
        response = ApiResponse(**data)
        
        assert response.code == "TEST_001"
        assert response.message == "测试消息"
        assert response.data == {"test": "value"}
        assert response.trace_id == "manual_trace_id"

    @patch("yai_nexus_api_middleware.responses.trace_context.get_trace_id")
    def test_trace_id_自动注入(self, mock_trace_id):
        """测试 trace_id 自动注入到响应中"""
        # 测试不同的 trace_id 值
        test_cases = ["trace_1", "trace_2", None, ""]
        
        for trace_id in test_cases:
            mock_trace_id.return_value = trace_id
            
            success_response = ApiResponse.success()
            failure_response = ApiResponse.failure(code="ERR", message="test")
            
            assert success_response.trace_id == trace_id
            assert failure_response.trace_id == trace_id