namespace Models
{
    public class RoleBlock
    {
        public string Title { get; set; } = string.Empty;

        public string Date { get; set; } = string.Empty;
        
        public List<string> Bullets { get; set; } = new();
    }
}
