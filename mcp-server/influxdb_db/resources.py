"""
InfluxDB resources for the MCP server
"""

import json

from mcp.server.fastmcp import FastMCP


def register_influxdb_resources(mcp: FastMCP):
    """Register InfluxDB-related resources with the MCP server"""

    @mcp.resource("influxdb://info")
    async def influxdb_server_info() -> str:
        """Get InfluxDB server information"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager

        if influxdb_manager is None:
            return json.dumps(
                {
                    "error": "InfluxDB is disabled. Please enable it in configuration to use this resource."
                },
                indent=2,
            )

        try:
            info = await influxdb_manager.get_server_info()
            return json.dumps({"server_info": info}, indent=2, default=str)
        except Exception as e:
            return json.dumps(
                {"error": f"Failed to get InfluxDB server info: {str(e)}"}, indent=2
            )

    @mcp.resource("influxdb://buckets")
    async def influxdb_buckets() -> str:
        """List all InfluxDB buckets"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager

        if influxdb_manager is None:
            return json.dumps(
                {
                    "error": "InfluxDB is disabled. Please enable it in configuration to use this resource."
                },
                indent=2,
            )

        try:
            buckets = await influxdb_manager.get_buckets()
            return json.dumps({"buckets": buckets}, indent=2, default=str)
        except Exception as e:
            return json.dumps(
                {"error": f"Failed to list InfluxDB buckets: {str(e)}"}, indent=2
            )

    @mcp.resource("influxdb://buckets/{bucket}/measurements")
    async def influxdb_measurements(bucket: str) -> str:
        """List measurements in an InfluxDB bucket (last 1 hour)"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager

        if influxdb_manager is None:
            return json.dumps(
                {
                    "error": "InfluxDB is disabled. Please enable it in configuration to use this resource."
                },
                indent=2,
            )

        try:
            measurements = await influxdb_manager.get_measurements(bucket, "-1h")
            return json.dumps(
                {"bucket": bucket, "measurements": measurements, "time_range": "-1h"},
                indent=2,
            )
        except Exception as e:
            return json.dumps(
                {"error": f"Failed to list InfluxDB measurements: {str(e)}"}, indent=2
            )

    @mcp.resource("influxdb://buckets/{bucket}/measurements/{measurement}/fields")
    async def influxdb_measurement_fields(bucket: str, measurement: str) -> str:
        """Get fields for an InfluxDB measurement (last 1 hour)"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager

        if influxdb_manager is None:
            return json.dumps(
                {
                    "error": "InfluxDB is disabled. Please enable it in configuration to use this resource."
                },
                indent=2,
            )

        try:
            fields = await influxdb_manager.get_fields(bucket, measurement, "-1h")
            return json.dumps(
                {
                    "bucket": bucket,
                    "measurement": measurement,
                    "fields": fields,
                    "time_range": "-1h",
                },
                indent=2,
                default=str,
            )
        except Exception as e:
            return json.dumps(
                {"error": f"Failed to get InfluxDB fields: {str(e)}"}, indent=2
            )

    @mcp.resource("influxdb://buckets/{bucket}/measurements/{measurement}/tags")
    async def influxdb_measurement_tags(bucket: str, measurement: str) -> str:
        """Get tag keys for an InfluxDB measurement (last 1 hour)"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager

        if influxdb_manager is None:
            return json.dumps(
                {
                    "error": "InfluxDB is disabled. Please enable it in configuration to use this resource."
                },
                indent=2,
            )

        try:
            tags = await influxdb_manager.get_tags(bucket, measurement, "-1h")
            return json.dumps(
                {
                    "bucket": bucket,
                    "measurement": measurement,
                    "tags": tags,
                    "time_range": "-1h",
                },
                indent=2,
                default=str,
            )
        except Exception as e:
            return json.dumps(
                {"error": f"Failed to get InfluxDB tags: {str(e)}"}, indent=2
            )

    @mcp.resource(
        "influxdb://buckets/{bucket}/measurements/{measurement}/tags/{tag_key}/values"
    )
    async def influxdb_tag_values(bucket: str, measurement: str, tag_key: str) -> str:
        """Get values for an InfluxDB tag key (last 1 hour)"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager

        if influxdb_manager is None:
            return json.dumps(
                {
                    "error": "InfluxDB is disabled. Please enable it in configuration to use this resource."
                },
                indent=2,
            )

        try:
            values = await influxdb_manager.get_tag_values(
                bucket, measurement, tag_key, "-1h"
            )
            return json.dumps(
                {
                    "bucket": bucket,
                    "measurement": measurement,
                    "tag_key": tag_key,
                    "values": values,
                    "time_range": "-1h",
                },
                indent=2,
            )
        except Exception as e:
            return json.dumps(
                {"error": f"Failed to get InfluxDB tag values: {str(e)}"}, indent=2
            )

    @mcp.resource("influxdb://buckets/{bucket}/measurements/{measurement}/sample")
    async def influxdb_sample_data(bucket: str, measurement: str) -> str:
        """Get sample data from an InfluxDB measurement (last 1 hour, limit 10)"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager

        if influxdb_manager is None:
            return json.dumps(
                {
                    "error": "InfluxDB is disabled. Please enable it in configuration to use this resource."
                },
                indent=2,
            )

        try:
            data = await influxdb_manager.get_sample_data(
                bucket, measurement, 10, "-1h"
            )
            return json.dumps(
                {
                    "bucket": bucket,
                    "measurement": measurement,
                    "sample_data": data,
                    "limit": 10,
                    "time_range": "-1h",
                },
                indent=2,
                default=str,
            )
        except Exception as e:
            return json.dumps(
                {"error": f"Failed to get InfluxDB sample data: {str(e)}"}, indent=2
            )
