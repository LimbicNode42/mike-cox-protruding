"""
InfluxDB tools for the MCP server
"""
from mcp.server.fastmcp import FastMCP
import json


def register_influxdb_tools(mcp: FastMCP):
    """Register InfluxDB-related tools with the MCP server"""
    
    @mcp.tool()
    async def influxdb_server_info() -> str:
        """Get InfluxDB server information"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager
        try:
            info = await influxdb_manager.get_server_info()
            return f"InfluxDB server info: {json.dumps(info, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get InfluxDB server info: {str(e)}"
    
    @mcp.tool()
    async def influxdb_list_buckets() -> str:
        """List all InfluxDB buckets"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager
        try:
            buckets = await influxdb_manager.get_buckets()
            return f"InfluxDB buckets: {json.dumps(buckets, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to list InfluxDB buckets: {str(e)}"
    
    @mcp.tool()
    async def influxdb_list_measurements(bucket: str, start_time: str = "-1h") -> str:
        """List measurements in an InfluxDB bucket"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager
        try:
            measurements = await influxdb_manager.get_measurements(bucket, start_time)
            return f"InfluxDB measurements in bucket '{bucket}': {measurements}"
        except Exception as e:
            return f"Failed to list InfluxDB measurements: {str(e)}"
    
    @mcp.tool()
    async def influxdb_get_fields(bucket: str, measurement: str, start_time: str = "-1h") -> str:
        """Get fields for an InfluxDB measurement"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager
        try:
            fields = await influxdb_manager.get_fields(bucket, measurement, start_time)
            return f"InfluxDB fields in '{measurement}': {json.dumps(fields, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get InfluxDB fields: {str(e)}"
    
    @mcp.tool()
    async def influxdb_get_tags(bucket: str, measurement: str, start_time: str = "-1h") -> str:
        """Get tag keys for an InfluxDB measurement"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager
        try:
            tags = await influxdb_manager.get_tags(bucket, measurement, start_time)
            return f"InfluxDB tags in '{measurement}': {json.dumps(tags, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get InfluxDB tags: {str(e)}"
    
    @mcp.tool()
    async def influxdb_get_tag_values(bucket: str, measurement: str, tag_key: str, start_time: str = "-1h") -> str:
        """Get values for an InfluxDB tag key"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager
        try:
            values = await influxdb_manager.get_tag_values(bucket, measurement, tag_key, start_time)
            return f"InfluxDB tag '{tag_key}' values: {values}"
        except Exception as e:
            return f"Failed to get InfluxDB tag values: {str(e)}"
    
    @mcp.tool()
    async def influxdb_query(bucket: str, flux_query: str) -> str:
        """Execute a Flux query on InfluxDB"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager
        try:
            results = await influxdb_manager.query_data(bucket, flux_query)
            return f"InfluxDB query results: {json.dumps(results, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to execute InfluxDB query: {str(e)}"
    
    @mcp.tool()
    async def influxdb_sample_data(bucket: str, measurement: str, limit: int = 10, start_time: str = "-1h") -> str:
        """Get sample data from an InfluxDB measurement"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager
        try:
            data = await influxdb_manager.get_sample_data(bucket, measurement, limit, start_time)
            return f"InfluxDB sample data from '{measurement}': {json.dumps(data, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get InfluxDB sample data: {str(e)}"
