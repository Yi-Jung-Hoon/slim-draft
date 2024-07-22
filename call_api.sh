#!/bin/bash
curl -X POST "http://localhost:8000/api/v1/batch/statistics/roi_stats" >> ./api_call.log 2>&1
echo "Executed at: $(date)" >> ./api_call.log