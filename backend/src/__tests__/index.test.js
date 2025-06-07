const request = require('supertest');
const app = require('../index');

describe('Server Health Check', () => {
  it('should return 200 OK for health check endpoint', async () => {
    const response = await request(app).get('/health');
    expect(response.status).toBe(200);
    expect(response.body).toEqual({ status: 'ok' });
  });

  it('should handle rate limiting', async () => {
    // Make multiple requests to trigger rate limit
    const requests = Array(101).fill().map(() => 
      request(app).get('/health')
    );
    
    const responses = await Promise.all(requests);
    const tooManyRequests = responses.filter(res => res.status === 429);
    
    expect(tooManyRequests.length).toBeGreaterThan(0);
  });
}); 