<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260314000000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Drop raw_scraped_datas table (Entity unused, dead code removed)';
    }

    public function up(Schema $schema): void
    {
        $this->addSql('DROP TABLE IF EXISTS raw_scraped_datas');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('CREATE TABLE raw_scraped_datas (id INT AUTO_INCREMENT NOT NULL, source_url VARCHAR(500) NOT NULL, raw_data LONGTEXT NOT NULL, scraped_at DATETIME NOT NULL COMMENT \'(DC2Type:datetime_immutable)\', processed TINYINT(1) DEFAULT 0 NOT NULL, error_message LONGTEXT DEFAULT NULL, PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
    }
}
