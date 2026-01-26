# AWS Bedrock Models by Region - Coding Focus

Reference guide for the best coding models available across AWS regions.

## Quick Reference: Best Coding Models

### 🏆 Tier 1: Maximum Context & Capability

| Model | Context | Best For | Regions |
|-------|---------|----------|---------|
| **Claude Opus 4.5** | 200K | Complex reasoning, large codebases | All major regions |
| **Claude Sonnet 4.5** | 200K | Fast coding, balanced performance | All major regions |
| **Nova Premier** | 1000K | Massive context (1M tokens) | us-east-1, us-west-2 |

### 🎯 Tier 2: Specialized Coding

| Model | Context | Best For | Regions |
|-------|---------|----------|---------|
| **Qwen3-Coder 480B** | 32K | Specialized coding tasks | us-west-2, ap-northeast-1 |
| **Qwen3-Coder 30B** | 32K | Efficient coding | Most regions |
| **DeepSeek R1** | 64K | Reasoning-focused coding | us-east-1 |

## Regional Availability

### us-east-1 (N. Virginia) ⭐ Most Complete
```
Top Coding Models:
- anthropic.claude-opus-4-5-20251101-v1:0          (200K context)
- anthropic.claude-sonnet-4-5-20250929-v1:0        (200K context)
- amazon.nova-premier-v1:0                         (1000K context)
- amazon.nova-premier-v1:0:1000k                   (1000K context)
- qwen.qwen3-coder-30b-a3b-v1:0                    (32K context)
- deepseek.r1-v1:0                                 (64K context)
```

**Recommendation**: Claude Opus 4.5 or Nova Premier for maximum capability

### us-west-2 (Oregon) ⭐ Best for Qwen
```
Top Coding Models:
- anthropic.claude-opus-4-5-20251101-v1:0          (200K context)
- anthropic.claude-sonnet-4-5-20250929-v1:0        (200K context)
- amazon.nova-premier-v1:0                         (1000K context)
- qwen.qwen3-coder-480b-a35b-v1:0                  (32K context) ⭐ EXCLUSIVE
- qwen.qwen3-coder-30b-a3b-v1:0                    (32K context)
```

**Recommendation**: Qwen3-Coder 480B for specialized coding, Claude Opus 4.5 for general

### eu-west-1 (Ireland)
```
Top Coding Models:
- anthropic.claude-opus-4-5-20251101-v1:0          (200K context)
- anthropic.claude-sonnet-4-5-20250929-v1:0        (200K context)
- qwen.qwen3-coder-30b-a3b-v1:0                    (32K context)
```

**Recommendation**: Claude Opus 4.5

### eu-central-1 (Frankfurt)
```
Top Coding Models:
- anthropic.claude-opus-4-5-20251101-v1:0          (200K context)
- anthropic.claude-sonnet-4-5-20250929-v1:0        (200K context)
- qwen.qwen3-coder-30b-a3b-v1:0                    (32K context)
```

**Recommendation**: Claude Opus 4.5

### ap-northeast-1 (Tokyo) ⭐ Best for Asia
```
Top Coding Models:
- anthropic.claude-opus-4-5-20251101-v1:0          (200K context)
- anthropic.claude-sonnet-4-5-20250929-v1:0        (200K context)
- qwen.qwen3-coder-480b-a35b-v1:0                  (32K context) ⭐
- qwen.qwen3-coder-30b-a3b-v1:0                    (32K context)
```

**Recommendation**: Qwen3-Coder 480B or Claude Opus 4.5

### ap-southeast-1 (Singapore)
```
Top Coding Models:
- anthropic.claude-opus-4-5-20251101-v1:0          (200K context)
- anthropic.claude-sonnet-4-5-20250929-v1:0        (200K context)
```

**Recommendation**: Claude Opus 4.5

## Model Comparison

### Claude Opus 4.5
- **Context**: 200K tokens
- **Strengths**: Best reasoning, complex problem solving, large codebase understanding
- **Use Case**: Architecture design, refactoring, complex debugging
- **Cost**: Highest
- **Speed**: Slower

### Claude Sonnet 4.5
- **Context**: 200K tokens
- **Strengths**: Fast, excellent coding, good balance
- **Use Case**: Day-to-day coding, rapid iteration
- **Cost**: Medium
- **Speed**: Fast

### Nova Premier
- **Context**: 1,000K tokens (1M!)
- **Strengths**: Massive context window
- **Use Case**: Entire large codebases, extensive documentation
- **Cost**: High
- **Speed**: Medium
- **Availability**: US regions only

### Qwen3-Coder 480B
- **Context**: 32K tokens
- **Strengths**: Purpose-built for coding, excellent code generation
- **Use Case**: Code completion, generation, translation
- **Cost**: Medium
- **Speed**: Fast
- **Availability**: us-west-2, ap-northeast-1 only

### Qwen3-Coder 30B
- **Context**: 32K tokens
- **Strengths**: Efficient, good for focused tasks
- **Use Case**: Smaller coding tasks, cost-effective
- **Cost**: Low
- **Speed**: Very fast

## Configuration Examples

### For Bedrock Chat (cdk.json)

#### Maximum Capability (eu-central-1)
```json
{
  "bedrockRegion": "eu-central-1",
  "defaultModel": "anthropic.claude-opus-4-5-20251101-v1:0",
  "titleModel": "anthropic.claude-3-5-haiku-20241022-v1:0"
}
```

#### Balanced Performance (us-east-1)
```json
{
  "bedrockRegion": "us-east-1",
  "defaultModel": "anthropic.claude-sonnet-4-5-20250929-v1:0",
  "titleModel": "amazon.nova-micro-v1:0"
}
```

#### Maximum Context (us-west-2)
```json
{
  "bedrockRegion": "us-west-2",
  "defaultModel": "amazon.nova-premier-v1:0:1000k",
  "titleModel": "amazon.nova-micro-v1:0"
}
```

#### Specialized Coding (us-west-2)
```json
{
  "bedrockRegion": "us-west-2",
  "defaultModel": "qwen.qwen3-coder-480b-a35b-v1:0",
  "titleModel": "amazon.nova-micro-v1:0"
}
```

## How to Check Your Region

```bash
# List all models in your region
aws bedrock list-foundation-models --region YOUR_REGION

# Filter for coding models
aws bedrock list-foundation-models --region YOUR_REGION \
  --query 'modelSummaries[?contains(modelId, `claude-opus`) || contains(modelId, `coder`) || contains(modelId, `nova-premier`)].{ID:modelId, Name:modelName}' \
  --output table
```

## Recommendations by Use Case

### Large Enterprise Codebase
- **Primary**: Claude Opus 4.5 (all regions)
- **Alternative**: Nova Premier (US only)
- **Reason**: Maximum context and reasoning capability

### Fast Development Iteration
- **Primary**: Claude Sonnet 4.5 (all regions)
- **Alternative**: Qwen3-Coder 480B (us-west-2, ap-northeast-1)
- **Reason**: Speed + quality balance

### Cost-Optimized
- **Primary**: Qwen3-Coder 30B (most regions)
- **Alternative**: Claude Sonnet 4.5
- **Reason**: Lower cost, still capable

### Massive Context Needs
- **Primary**: Nova Premier 1000K (us-east-1, us-west-2)
- **Alternative**: Claude Opus 4.5
- **Reason**: 1M token context window

## Notes

- All Claude models support 200K context
- Nova Premier supports up to 1M tokens (US regions only)
- Qwen3-Coder 480B only available in us-west-2 and ap-northeast-1
- DeepSeek R1 only available in us-east-1
- **IMPORTANT**: Models must be enabled in Bedrock Console > Model Access before use
- Model availability changes frequently - verify with AWS CLI

## Troubleshooting

### "Invalid Model ID" Error

If you get an invalid model ID error:

1. Verify the model is available in your region:
   ```bash
   aws bedrock list-foundation-models --region YOUR_REGION --query 'modelSummaries[?modelId==`MODEL_ID`]'
   ```

2. Enable model access in Bedrock Console:
   - Go to: https://console.aws.amazon.com/bedrock/home?region=YOUR_REGION#/modelaccess
   - Click "Manage model access"
   - Find and enable the model
   - Save changes (may take a few minutes)

3. Verify model access is granted:
   ```bash
   aws bedrock get-foundation-model --model-identifier MODEL_ID --region YOUR_REGION
   ```

## Last Updated
Generated: 2025-01-11
