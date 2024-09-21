using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;


namespace TrustIndicator_Backend.Controllers
{
    public class User
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Email { get; set; }
        public string Password { get; set; }
    }


    [Route("api/[controller]")]
    [ApiController]
    public class UserController : ControllerBase
    {

        private static List<User> users = new List<User>
        {
            new User { Id = 0, Name = "Admin", Email = "trustindicator@gmail.com", Password = "123" }
        };

        [HttpGet]
        public ActionResult<IEnumerable<User>> GetUsers()
        {
            return Ok(users);
        }


        [HttpGet("{id}")]
        public ActionResult<User> GetUser(int id)
        {
            var user = users.FirstOrDefault(u => u.Id == id);
            if (user == null)
                return NotFound();
            return Ok(user);
        }


        [HttpPost]
        public ActionResult<User> CreateUser(User user)
        {
            user.Id = users.Max(u => u.Id) + 1;
            users.Add(user);
            return CreatedAtAction(nameof(GetUser), new { id = user.Id }, user);
        }


        [HttpPut("{id}")]
        public IActionResult UpdateUser(int id, User user)
        {
            var existingUser = users.FirstOrDefault(u => u.Id == id);
            if (existingUser == null)
                return NotFound();
            existingUser.Name = user.Name;
            existingUser.Email = user.Email;
            return NoContent();
        }


        [HttpDelete("{id}")]
        public IActionResult DeleteUser(int id)
        {
            var user = users.FirstOrDefault(u => u.Id == id);
            if (user == null)
                return NotFound();
            users.Remove(user);
            return NoContent();
        }


    }
}
